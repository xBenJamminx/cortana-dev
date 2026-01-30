// ==UserScript==
// @name         TweetXer
// @namespace    https://github.com/lucahammer/tweetXer/
// @version      0.9.4
// @description  Delete all your Tweets for free.
// @author       Luca,dbort,pReya,Micolithe,STrRedWolf
// @license      NoHarm-draft
// @match        https://x.com/*
// @match        https://mobile.x.com/*
// @match        https://twitter.com/*
// @match        https://mobile.twitter.com/*
// @icon         https://www.google.com/s2/favicons?domain=twitter.com
// @grant        none
// @run-at       document-idle
// @downloadURL  https://update.greasyfork.org/scripts/476062/TweetXer.user.js
// @updateURL    https://update.greasyfork.org/scripts/476062/TweetXer.meta.js
// @supportURL   https://github.com/lucahammer/tweetXer/issues
// ==/UserScript==

(function () {
    let TweetsXer = {
        version: '0.9.4',
        TweetCount: 0,
        dId: "exportUpload",
        tIds: [],
        tId: "",
        ratelimitreset: 0,
        more: '[data-testid="tweet"] [data-testid="caret"]',
        skip: 0,
        total: 0,
        dCount: 0,
        deleteURL: '/i/api/graphql/VaenaVgh5q5ih7kvyVjgtg/DeleteTweet',
        unfavURL: '/i/api/graphql/ZYKSe-w7KEslx3JhSIk5LA/UnfavoriteTweet',
        deleteMessageURL: '/i/api/graphql/BJ6DtxA2llfjnRoRjaiIiw/DMMessageDeleteMutation',
        deleteConvoURL: '/i/api/1.1/dm/conversation/USER_ID-CONVERSATION_ID/delete.json',
        deleteDMsOneByOne: false,
        username: '',
        action: '',
        bookmarksURL: '/i/api/graphql/L7vvM2UluPgWOW4GDvWyvw/Bookmarks?',
        bookmarks: [],
        bookmarksNext: '',
        baseUrl: 'https://x.com',
        authorization: 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        ct0: false,
        transaction_id: '',

        async init() {
            this.baseUrl = `https://${window.location.hostname}`
            this.updateTransactionId()
            this.createUploadForm()
            await this.getTweetCount()
            this.ct0 = this.getCookie('ct0')
            this.username = document.location.href.split('/')[3].replace('#', '')
        },

        sleep(ms) {
            return new Promise((resolve) => setTimeout(resolve, ms))
        },

        getCookie(name) {
            const match = `; ${document.cookie}`.match(`;\\s*${name}=([^;]+)`)
            return match ? match[1] : null
        },

        updateTransactionId() {
            this.transaction_id = [...crypto.getRandomValues(new Uint8Array(95))]
                .map((x, i) => (i = x / 255 * 61 | 0, String.fromCharCode(i + (i > 9 ? i > 35 ? 61 : 55 : 48)))).join``
        },

        updateTitle(text) {
            document.getElementById('tweetsXer_title').textContent = text
        },

        updateInfo(text) {
            document.getElementById("info").textContent = text
        },

        createProgressBar() {
            const progressbar = document.createElement("progress")
            progressbar.id = "progressbar"
            progressbar.value = this.dCount
            progressbar.max = this.total
            progressbar.style = 'width:100%'
            document.getElementById(this.dId).appendChild(progressbar)
        },

        updateProgressBar() {
            document.getElementById('progressbar').value = this.dCount
            this.updateInfo(`${this.dCount} deleted. ${this.tId}`)
        },

        processFile() {
            const tn = document.getElementById(`${TweetsXer.dId}_file`)
            if (tn.files && tn.files[0]) {
                let fr = new FileReader()
                fr.onloadend = function (evt) {
                    let cutpoint = evt.target.result.indexOf('= ')
                    let filestart = evt.target.result.slice(0, cutpoint)
                    let json = JSON.parse(evt.target.result.slice(cutpoint + 1))

                    if (filestart.includes('.tweet_headers.') || filestart.includes('.tweets.') || filestart.includes('.tweet.')) {
                        console.log('File contains Tweets.')
                        TweetsXer.action = 'untweet'
                        TweetsXer.tIds = json.map((x) => x.tweet.tweet_id || x.tweet.id_str)
                    } else if (filestart.includes('.like.')) {
                        console.log('File contains Favs.')
                        TweetsXer.action = 'unfav'
                        TweetsXer.tIds = json.map((x) => x.like.tweetId)
                    }

                    if (TweetsXer.action.length > 0) {
                        TweetsXer.total = TweetsXer.tIds.length
                        document.getElementById(`${TweetsXer.dId}_file`).remove()
                        TweetsXer.createProgressBar()
                    }

                    if (TweetsXer.action == 'untweet') {
                        TweetsXer.skip = TweetsXer.total - TweetsXer.TweetCount - parseInt(TweetsXer.total / 20)
                        TweetsXer.skip = Math.max(0, TweetsXer.skip)
                        TweetsXer.tIds.reverse()
                        TweetsXer.tIds = TweetsXer.tIds.slice(TweetsXer.skip)
                        TweetsXer.dCount = TweetsXer.skip
                        TweetsXer.tIds.reverse()
                        TweetsXer.updateTitle(`TweetXer: Deleting ${TweetsXer.total} Tweets`)
                        TweetsXer.deleteTweets()
                    } else if (TweetsXer.action == 'unfav') {
                        TweetsXer.updateTitle(`TweetXer: Deleting ${TweetsXer.total} Favs`)
                        TweetsXer.deleteFavs()
                    }
                }
                fr.readAsText(tn.files[0])
            }
        },

        createUploadForm() {
            const h2Class = document.querySelectorAll("h2")[1]?.getAttribute("class") || ""
            const div = document.createElement("div")
            div.id = this.dId
            if (document.getElementById(this.dId)) { document.getElementById(this.dId).remove() }
            div.innerHTML = `
            <style>#${this.dId}{ z-index:99999; position: sticky; top:0px; left:0px; width:auto; margin:0 auto; padding: 20px 10%; background:#87CEFA; opacity:0.95; } #${this.dId} > *{padding:5px;} button{background-color:#eff3f4;border-radius:666px;padding:2px 10px;} a {color:blue;}</style>
            <div style="color:black">
                <h2 class="${h2Class}" id="tweetsXer_title">TweetXer</h2>
                <p id="info">Please wait for your profile to load.</p>
                <p id="start">
                    <input type="file" value="" id="${this.dId}_file"  />
                    <a href="#" id="toggleAdvanced">Advanced Options</a>
                <div id="advanced" style="display:none">
                    <label for="skipCount">Skip this many Tweets:</label>
                    <input id="skipCount" type="number" value="" />
                    <p><strong>No archive file?</strong><br>
                        <button id="slowDelete" type="button">Slow delete without file</button>
                    </p>
                    <p><a id="removeTweetXer" href="#">Remove TweetXer</a></p>
                </div>
            </div>`
            document.body.insertBefore(div, document.body.firstChild)
            document.getElementById("toggleAdvanced").addEventListener("click", (() => {
                const adv = document.getElementById('advanced')
                adv.style.display = adv.style.display == 'none' ? 'block' : 'none'
            }))
            document.getElementById(`${this.dId}_file`).addEventListener("change", this.processFile, false)
            document.getElementById("slowDelete").addEventListener("click", this.slowDelete, false)
            document.getElementById("removeTweetXer").addEventListener("click", this.removeTweetXer, false)
        },

        async sendRequest(url, body) {
            return new Promise(async (resolve) => {
                try {
                    let response = await fetch(url, {
                        "headers": {
                            "authorization": TweetsXer.authorization,
                            "content-type": "application/json",
                            "x-client-transaction-id": TweetsXer.transaction_id,
                            "x-csrf-token": TweetsXer.ct0,
                            "x-twitter-active-user": "yes",
                            "x-twitter-auth-type": "OAuth2Session"
                        },
                        "referrer": `${TweetsXer.baseUrl}/${TweetsXer.username}/with_replies`,
                        "body": body || `{"variables":{"tweet_id":"${TweetsXer.tId}","dark_request":false},"queryId":"${url.split('/')[6]}"}`,
                        "method": "POST",
                        "mode": "cors",
                        "credentials": "include",
                        "signal": AbortSignal.timeout(5000)
                    })

                    if (response.status == 200) {
                        TweetsXer.dCount++
                        TweetsXer.updateProgressBar()
                        if (response.headers.get('x-rate-limit-remaining') != null && response.headers.get('x-rate-limit-remaining') < 1) {
                            TweetsXer.ratelimitreset = response.headers.get('x-rate-limit-reset')
                            let sleeptime = TweetsXer.ratelimitreset - Math.floor(Date.now() / 1000)
                            while (sleeptime > 0) {
                                sleeptime = TweetsXer.ratelimitreset - Math.floor(Date.now() / 1000)
                                TweetsXer.updateInfo(`Ratelimited. Waiting ${sleeptime}s. ${TweetsXer.dCount} deleted.`)
                                await TweetsXer.sleep(1000)
                            }
                        }
                        resolve('deleted')
                    } else if (response.status == 429) {
                        TweetsXer.tIds.push(TweetsXer.tId)
                        await TweetsXer.sleep(1000)
                    }
                } catch (error) {
                    TweetsXer.tIds.push(TweetsXer.tId)
                    resolve('error')
                }
            })
        },

        async deleteTweets() {
            while (this.tIds.length > 0) {
                this.tId = this.tIds.pop()
                await this.sendRequest(this.baseUrl + this.deleteURL)
            }
            this.tId = ''
            this.updateProgressBar()
        },

        async deleteFavs() {
            while (this.tIds.length > 0) {
                this.tId = this.tIds.pop()
                await this.sendRequest(this.baseUrl + this.unfavURL)
            }
            this.tId = ''
            this.updateProgressBar()
        },

        async getTweetCount() {
            await this.sleep(1000)
            try {
                let countText = document.querySelector('[data-testid="primaryColumn"]>div>div>div')?.textContent
                if (!countText) countText = document.querySelector('[data-testid="TopNavBar"]>div>div')?.textContent
                let match = countText?.match(/((\d|,|\.|K)+)/)
                TweetsXer.TweetCount = match ? parseInt(match[1].replace(/,/g, '')) : 1000000
            } catch {
                TweetsXer.TweetCount = 1000000
            }
            this.updateInfo('Select your tweet-headers.js from your Twitter Data Export to start deletion.')
        },

        async slowDelete() {
            document.getElementById('start').remove()
            TweetsXer.total = TweetsXer.TweetCount
            TweetsXer.createProgressBar()
            document.querySelectorAll('[data-testid="ScrollSnap-List"] a')[1].click()
            await TweetsXer.sleep(2000)

            let consecutiveErrors = 0
            const more = '[data-testid="tweet"] [data-testid="caret"]'

            while (document.querySelectorAll(more).length > 0) {
                await TweetsXer.sleep(1200)
                document.querySelectorAll('section [data-testid="cellInnerDiv"]>div>div>div').forEach(x => x.remove())
                
                try {
                    const moreElement = document.querySelector(more)
                    if (moreElement) moreElement.scrollIntoView({'behavior': 'smooth'})

                    // Unretweet if retweet
                    let unretweet = document.querySelector('[data-testid="unretweet"]')
                    if (unretweet) {
                        unretweet.click()
                        let confirmURT = await waitForElemToExist('[data-testid="unretweetConfirm"]')
                        confirmURT.click()
                    } else {
                        // Delete tweet
                        let caret = await waitForElemToExist(more)
                        caret.click()
                        let menu = await waitForElemToExist('[role="menuitem"]')
                        if (!menu.textContent.includes('@')) {
                            menu.click()
                            let confirmation = await waitForElemToExist('[data-testid="confirmationSheetConfirm"]')
                            if (confirmation) confirmation.click()
                        } else {
                            caret.click()
                            document.querySelector('[data-testid="tweet"]').remove()
                        }
                    }

                    TweetsXer.dCount++
                    TweetsXer.updateProgressBar()
                    consecutiveErrors = 0
                    if (TweetsXer.dCount % 100 == 0) console.log(`${new Date().toUTCString()} Deleted ${TweetsXer.dCount} Tweets`)
                } catch (error) {
                    consecutiveErrors++
                    if (consecutiveErrors >= 5) break
                }
            }
            console.log(`Finished. Total deleted: ${TweetsXer.dCount} Tweets.`)
        },

        removeTweetXer() {
            document.getElementById('exportUpload').remove()
        }
    }

    const waitForElemToExist = async (selector) => {
        const elem = document.querySelector(selector)
        if (elem) return elem
        return new Promise(resolve => {
            const observer = new MutationObserver(() => {
                const elem = document.querySelector(selector)
                if (elem) {
                    resolve(elem)
                    observer.disconnect()
                }
            })
            observer.observe(document.body, { subtree: true, childList: true })
        })
    }

    TweetsXer.init()
})()
