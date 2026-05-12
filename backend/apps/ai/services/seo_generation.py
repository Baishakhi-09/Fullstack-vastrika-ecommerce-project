from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class AISEOService:
    @staticmethod
    def generate_meta_title(product_name, description):
        prompt = f"""
        Generate an SEO optimized product meta title.

        Product Name:
        {product_name}

        Description:
        {description}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content
    
    @staticmethod
    def generate_meta_description(product_name, description):
        prompt = f"""
        Generate an SEO optimized meta description.

        Product Name:
        {product_name}

        Description:
        {description}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content