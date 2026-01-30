#!/usr/bin/env python3
"""
Intelligent Image Generation Router
Routes image tasks to appropriate model based on complexity and use case
"""
import os
from typing import Literal, Optional
from dataclasses import dataclass

# Set up API keys
os.environ['GOOGLE_API_KEY'] = 'REDACTED_GOOGLE_API_KEY'

@dataclass
class ImageModelConfig:
    name: str
    provider: str
    model_id: str
    cost_per_image: float
    strengths: list[str]
    best_for: list[str]

class ImageRouter:
    def __init__(self):
        self.models = {
            # Simple/Bulk - Imagen 3 Fast
            'simple': ImageModelConfig(
                name='Imagen 3 Fast',
                provider='google',
                model_id='imagen-3-fast',
                cost_per_image=0.02,
                strengths=['speed', 'cost_efficiency', 'prototyping'],
                best_for=['logos', 'icons', 'simple_graphics', 'placeholders', 'bulk_generation']
            ),
            # Standard quality - Imagen 3 Standard  
            'standard': ImageModelConfig(
                name='Imagen 3 Standard',
                provider='google',
                model_id='imagen-3-standard',
                cost_per_image=0.03,
                strengths=['best_text_rendering', 'photorealism', 'balanced_quality'],
                best_for=['marketing_materials', 'social_media', 'product_photos', 'text_heavy_images']
            ),
            # Complex/High-quality - Nano Banana Pro
            'complex': ImageModelConfig(
                name='Nano Banana Pro 2K',
                provider='google',
                model_id='gemini-3-pro-image-preview',  # Nano Banana uses Gemini 3 Pro Image
                cost_per_image=0.05,
                strengths=['4K_resolution', 'multilingual_text', 'ultra_detailed', 'realism'],
                best_for=['youtube_thumbnails', 'article_thumbnails', 'UGC', 'realistic_photos', 'print_materials', 'high_res_output']
            ),
            # Maximum quality - Nano Banana 4K
            'premium': ImageModelConfig(
                name='Nano Banana Pro 4K',
                provider='google',
                model_id='gemini-3-pro-image-preview',
                cost_per_image=0.15,
                strengths=['4K_native', 'maximum_detail', 'print_ready', 'multilingual'],
                best_for=['print_posters', 'billboards', 'premium_marketing', '4K_wallpapers']
            ),
        }
    
    def classify_complexity(self, prompt: str) -> Literal['simple', 'standard', 'complex', 'premium']:
        """Classify image generation task based on prompt"""
        prompt_lower = prompt.lower()
        
        # Premium indicators (4K, print, maximum quality)
        premium_keywords = [
            '4k', 'print', 'poster', 'billboard', 'ultra high res', 'maximum quality',
            'professional photo', 'studio quality', 'portfolio', 'gallery'
        ]
        
        # Complex indicators (thumbnails, UGC, realism)
        complex_keywords = [
            'youtube thumbnail', 'article thumbnail', 'ugc', 'realistic', 'photorealistic',
            'portrait', 'product shot', 'advertising', 'campaign', 'banner',
            'human face', 'detailed', 'intricate', 'cinematic', 'professional'
        ]
        
        # Simple indicators (logos, icons, basic)
        simple_keywords = [
            'logo', 'icon', 'simple', 'minimal', 'flat design', 'vector style',
            'basic', 'placeholder', 'draft', 'wireframe', 'sketch'
        ]
        
        # Check for premium
        if any(kw in prompt_lower for kw in premium_keywords):
            return 'premium'
        
        # Check for complex (thumbnails, UGC, realism)
        if any(kw in prompt_lower for kw in complex_keywords):
            return 'complex'
        
        # Check for simple
        if any(kw in prompt_lower for kw in simple_keywords):
            return 'simple'
        
        # Default to standard for most cases
        return 'standard'
    
    def route(self, prompt: str, force_model: Optional[str] = None) -> tuple[str, ImageModelConfig]:
        """Route image generation to appropriate model"""
        if force_model and force_model in self.models:
            return 'forced', self.models[force_model]
        
        complexity = self.classify_complexity(prompt)
        return complexity, self.models[complexity]
    
    def generate(self, prompt: str, force_model: Optional[str] = None) -> dict:
        """Generate image with intelligent routing"""
        classification, model_config = self.route(prompt, force_model)
        
        result = {
            'classification': classification,
            'model_used': model_config.name,
            'provider': model_config.provider,
            'cost': model_config.cost_per_image,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt
        }
        
        # Note: Actual generation would use Google's image generation API
        # For now, return the routing decision
        result['note'] = f"Would generate using {model_config.name} (${model_config.cost_per_image}/image)"
        result['success'] = True
        
        return result
    
    def estimate_cost(self, prompts: list[str]) -> dict:
        """Estimate cost for batch of image generations"""
        total_cost = 0
        breakdown = []
        
        for prompt in prompts:
            classification, model = self.route(prompt)
            total_cost += model.cost_per_image
            breakdown.append({
                'prompt': prompt[:50] + '...',
                'classification': classification,
                'model': model.name,
                'cost': model.cost_per_image
            })
        
        return {
            'total_images': len(prompts),
            'total_cost': total_cost,
            'breakdown': breakdown
        }

def demo():
    """Demo the image router"""
    router = ImageRouter()
    
    test_prompts = [
        "Simple flat logo for a tech startup",
        "YouTube thumbnail for a video about AI tools",
        "Realistic UGC-style photo of someone using a smartphone",
        "4K print-ready poster for a conference",
        "Social media graphic with text overlay",
        "Article thumbnail for blog post about productivity",
        "Minimal icon set for website",
        "Photorealistic portrait for advertising campaign",
        "Quick placeholder image for wireframe",
        "Instagram post with product photo"
    ]
    
    print("="*80)
    print("IMAGE GENERATION ROUTER")
    print("="*80)
    print()
    
    # Show individual routing
    print("ROUTING DECISIONS:")
    print("-"*80)
    for prompt in test_prompts:
        classification, model = router.route(prompt)
        print(f"\nPrompt: {prompt[:60]}...")
        print(f"  → {classification.upper()}")
        print(f"  → Model: {model.name}")
        print(f"  → Cost: ${model.cost_per_image}/image")
    
    print("\n" + "="*80)
    print("BATCH COST ESTIMATE:")
    print("-"*80)
    estimate = router.estimate_cost(test_prompts)
    print(f"Total images: {estimate['total_images']}")
    print(f"Total cost: ${estimate['total_cost']:.2f}")
    print(f"Average per image: ${estimate['total_cost']/estimate['total_images']:.3f}")
    
    print("\n" + "="*80)
    print("\nCOST COMPARISON (100 images each):")
    print("-"*80)
    simple_batch = ["simple logo"] * 100
    complex_batch = ["youtube thumbnail"] * 100
    
    simple_cost = router.estimate_cost(simple_batch)['total_cost']
    complex_cost = router.estimate_cost(complex_batch)['total_cost']
    
    print(f"100 Simple images (Imagen 3 Fast): ${simple_cost:.2f}")
    print(f"100 Complex images (Nano Banana 2K): ${complex_cost:.2f}")
    print(f"Savings with smart routing: ${complex_cost - simple_cost:.2f}")
    
    print("\n" + "="*80)
    print("\nUsage:")
    print("  from image_router import ImageRouter")
    print("  router = ImageRouter()")
    print("  result = router.generate('Your image prompt')")
    print("  # Then use Google API with result['model_used']")

if __name__ == "__main__":
    demo()
