# Intelligent Model Routing Setup Guide

## The Goal
Build an intelligent router that automatically routes tasks to the right AI model based on complexity, cost, and use case—saving 60-90% on API costs while improving output quality.

---

## Step 1: Audit Your Current Usage

**Before building anything, analyze your actual usage patterns:**

1. **Export your API logs** (OpenAI, Anthropic, Google, etc.)
2. **Categorize your prompts:**
   - Simple queries (facts, calculations, short answers)
   - Complex tasks (debugging, analysis, multi-step reasoning)
   - Expert work (architecture, research, creative writing)
   - Document processing (PDFs, long context, translations)
3. **Calculate current costs** per category
4. **Identify overpayment:** Are you using GPT-4/Opus for simple queries?

---

## Step 2: Research Available Models (2025 Landscape)

### Frontier Models (High Cost, Maximum Capability)
| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| Claude Opus 4.5 | $15.00 | $75.00 | Novels, research, maximum quality |
| GPT-5.2 | $1.75 | $14.00 | Deep reasoning, complex coding |
| Gemini 3 Pro | $3.50 | $10.50 | Multimodal, agentic workflows |

### Mid-Tier (Balanced Quality/Cost)
| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| Claude Sonnet 4.5 | $3.00 | $15.00 | General tasks, coding |
| Gemini 3 Flash | $0.15 | $0.60 | Speed, simple tasks, prototyping |
| GPT-4o | $2.50 | $10.00 | General purpose |

### Budget/Specialized (Low Cost, Specific Use)
| Model | Input/1M | Output/1M | Best For |
|-------|----------|-----------|----------|
| Kimi K2.5 | $0.50 | $2.00 | Long context (200K), documents, Chinese |
| Gemini 2.5 Flash | $0.075 | $0.30 | Ultra-fast, simple queries |
| Imagen 3 Fast | $0.02/image | — | Bulk image generation |
| Nano Banana Pro | $0.05/image | — | 4K images, multilingual text |

---

## Step 3: Define Your Routing Logic

### Classification Framework

Create rules that classify tasks into tiers:

**SIMPLE Tier** → Cheapest model
- Keywords: "what is", "how to", "explain", "calculate", "convert"
- Length: < 15 words
- Examples: Facts, simple math, definitions
- Route to: Gemini Flash, GPT-3.5, local models

**COMPLEX Tier** → Mid-range model
- Keywords: "debug", "analyze", "refactor", "optimize", "implement"
- Length: 15-50 words
- Examples: Code debugging, feature implementation, analysis
- Route to: Sonnet, Gemini Pro, GPT-4o

**EXPERT Tier** → Premium model (but only when needed)
- Keywords: "architecture", "design a system", "novel", "research", "thesis"
- Length: > 50 words OR contains complex reasoning keywords
- Examples: System design, creative writing, deep research
- Route to: Opus, GPT-5.2, Gemini 3 Pro

**SPECIALIZED Tier** → Task-specific models
- Keywords: "document", "PDF", "translate", "chinese", "100 pages"
- Route to: Kimi (long context), Imagen (images), Whisper (audio)

### Keyword Detection Logic
```python
expert_keywords = [
    'architecture', 'design a system', 'distributed', 'microservices',
    'scalability', 'novel', 'book', 'research', 'thesis', 'dissertation',
    'complex algorithm', 'machine learning model', 'neural network',
    'whitepaper', 'framework', 'library', 'sdk', 'compiler',
    'economic implications', 'philosophical', 'consciousness'
]

complex_keywords = [
    'debug', 'refactor', 'optimize', 'analyze', 'compare',
    'multiple', 'integrate', 'api', 'database', 'authentication',
    'deploy', 'docker', 'kubernetes', 'pipeline', 'workflow',
    'component', 'feature', 'function', 'class', 'module',
    'write a', 'create a', 'build a', 'implement'
]

kimi_keywords = [
    'document', 'pdf', 'analyze this file', 'long text', 'transcript',
    'summarize this article', 'chinese', 'mandarin', 'translation',
    'book summary', 'research paper', 'contract', 'legal document',
    '100 pages', '1000 lines', 'large file', 'entire codebase'
]
```

---

## Step 4: Build the Router

### Core Architecture
```python
class ModelRouter:
    def __init__(self):
        self.models = {
            'simple': ModelConfig(name='Gemini Flash', cost=0.15),
            'complex': ModelConfig(name='Sonnet', cost=3.00),
            'expert': ModelConfig(name='GPT-5.2', cost=1.75),
            'kimi': ModelConfig(name='Kimi', cost=0.50)
        }
    
    def classify(self, task: str) -> str:
        # Implement keyword detection logic
        # Return: 'simple', 'complex', 'expert', or 'kimi'
        pass
    
    def route(self, task: str) -> ModelConfig:
        classification = self.classify(task)
        return self.models[classification]
```

### Key Design Decisions

1. **Word count + keywords** → More reliable than pure ML classification
2. **Rule-based first** → Easier to debug and modify than ML
3. **Override option** → Always allow `force_model='opus'` for exceptions
4. **Fallback chain** → If primary fails, try cheaper alternative

---

## Step 5: Cost Estimation & Monitoring

### Batch Cost Calculator
```python
def estimate_cost(self, tasks: list[str]) -> dict:
    total = 0
    breakdown = []
    for task in tasks:
        model = self.route(task)
        cost = model.cost * 0.001  # Assume 1K tokens
        total += cost
        breakdown.append({
            'task': task[:50],
            'model': model.name,
            'cost': cost
        })
    return {'total': total, 'breakdown': breakdown}
```

### Cost Comparison Matrix
Calculate your potential savings:

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| 1000 simple queries | Opus $15 | Flash $0.15 | 99% |
| 500 complex tasks | Opus $15 | Sonnet $3 | 80% |
| 200 expert tasks | Opus $15 | GPT-5.2 $1.75 | 88% |
| 100 documents | Opus $15 | Kimi $0.50 | 96% |

---

## Step 6: Image Generation Routing (Bonus)

Apply the same logic to image generation:

| Use Case | Model | Cost | Criteria |
|----------|-------|------|----------|
| Logos, icons, simple graphics | Imagen 3 Fast | $0.02 | "logo", "icon", "simple" |
| Social media, text overlays | Imagen 3 Standard | $0.03 | "social", "text", "marketing" |
| YouTube thumbnails, UGC | Nano Banana 2K | $0.05 | "thumbnail", "realistic", "ugc" |
| Print, 4K, premium | Nano Banana 4K | $0.15 | "4K", "print", "poster" |

---

## Step 7: Iterate & Refine

### Week 1: Baseline
- Route everything through router
- Log actual classifications vs expected
- Track costs

### Week 2: Tune
- Adjust keyword lists based on misclassifications
- Add new edge cases
- Fine-tune word count thresholds

### Week 3: Optimize
- Add caching for repeated queries
- Implement batch processing
- Add cost alerts/limits

---

## Common Pitfalls

1. **Over-optimization** → Don't route TOO granular (3-4 tiers max)
2. **Under-optimization** → Don't use one model for everything
3. **Wrong metrics** → Track quality AND cost, not just cost
4. **Ignoring latency** → Faster cheap model > slower expensive one
5. **Missing edge cases** → Always have force_model override

---

## Real-World Results

**Typical savings after implementation:**
- 60-90% cost reduction
- 2-3x faster responses for simple tasks
- Better outputs (right tool for the job)
- Zero decision fatigue

**The key insight:**
You're not just saving money—you're building an intelligent system that gets smarter about which AI to use, when.

---

## Quick-Start Template

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ModelConfig:
    name: str
    provider: str
    cost_input: float  # per 1M tokens
    cost_output: float

class ModelRouter:
    def __init__(self):
        self.models = {
            'simple': ModelConfig('Gemini Flash', 'google', 0.15, 0.60),
            'complex': ModelConfig('Claude Sonnet', 'anthropic', 3.00, 15.00),
            'expert': ModelConfig('GPT-5.2', 'openai', 1.75, 14.00),
            'kimi': ModelConfig('Kimi K2.5', 'moonshot', 0.50, 2.00)
        }
    
    def classify(self, task: str) -> Literal['simple', 'complex', 'expert', 'kimi']:
        task_lower = task.lower()
        
        # Check for expert-level work
        if any(kw in task_lower for kw in ['architecture', 'novel', 'research']):
            return 'expert'
        
        # Check for documents/long context
        if any(kw in task_lower for kw in ['pdf', 'document', '100 pages']):
            return 'kimi'
        
        # Check complexity
        if len(task.split()) <= 15:
            return 'simple'
        elif any(kw in task_lower for kw in ['debug', 'implement', 'build']):
            return 'complex'
        
        return 'expert'  # Default to safe option
    
    def route(self, task: str, force_model: str = None) -> ModelConfig:
        if force_model:
            return self.models[force_model]
        return self.models[self.classify(task)]

# Usage
router = ModelRouter()
model = router.route("Your task here")
print(f"Routing to: {model.name} (${model.cost_input}/1M)")
```

---

**Remember:** The goal isn't perfection on day one. Start with simple rules, measure results, iterate. Your router will get smarter as you use it.

*"Stop using a Ferrari to buy groceries."*
