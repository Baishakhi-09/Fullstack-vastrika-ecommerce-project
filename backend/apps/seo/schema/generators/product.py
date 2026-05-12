import json

class ProductSchemaGenerator:

    @staticmethod
    def generate(product):

        schema = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product.name,
            "description": product.meta_description,
            "sku": product.sku,
            "offers": {
                "@type": "Offer",
                "priceCurrency": "INR",
                "price": str(product.selling_price),
                "availability": "https://schema.org/InStock",
            },
        }

        return json.dumps(schema, indent=4)