"""
Layout Builder API Client
=========================

Client for interacting with Layout Builder v7.5-main API.
"""

import requests
from typing import Dict, Any, List


class LayoutBuilderClient:
    """Client for Layout Builder v7.5-main API"""

    def __init__(self, base_url: str = "https://web-production-f0d13.up.railway.app"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def get_api_info(self) -> Dict:
        """Get API information"""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()

    def get_layouts(self) -> Dict:
        """Get available layouts and specifications"""
        response = self.session.get(f"{self.base_url}/api/layouts")
        response.raise_for_status()
        return response.json()

    def create_presentation(self, title: str, slides: List[Dict]) -> Dict:
        """
        Create presentation

        Args:
            title: Presentation title
            slides: List of slide dicts. Each slide should have either:
                    - 'layout' and 'content' keys (proper format)
                    - OR just content fields (will be auto-wrapped)
        """
        # Ensure slides are in proper format with layout + content structure
        formatted_slides = []
        for slide in slides:
            if "layout" in slide and "content" in slide:
                # Already in correct format
                formatted_slides.append(slide)
            else:
                # Auto-detect layout from content and wrap it
                layout_id = slide.get("layout_id", "L01")  # Default to L01
                content = {k: v for k, v in slide.items() if k != "layout_id"}
                formatted_slides.append({
                    "layout": layout_id,
                    "content": content
                })

        data = {"title": title, "slides": formatted_slides}
        response = self.session.post(
            f"{self.base_url}/api/presentations",
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # Normalize response format (API returns 'id', but we want 'presentation_id')
        if "id" in result and "presentation_id" not in result:
            result["presentation_id"] = result["id"]

        return result

    def get_presentation(self, presentation_id: str) -> Dict:
        """Get presentation data"""
        response = self.session.get(
            f"{self.base_url}/api/presentations/{presentation_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def delete_presentation(self, presentation_id: str) -> Dict:
        """Delete presentation"""
        response = self.session.delete(
            f"{self.base_url}/api/presentations/{presentation_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_presentation_url(self, presentation_id: str) -> str:
        """Get viewable presentation URL"""
        return f"{self.base_url}/p/{presentation_id}"


if __name__ == "__main__":
    # Test client
    client = LayoutBuilderClient()

    print("🧪 Testing Layout Builder Client...")

    # Test API info
    info = client.get_api_info()
    print(f"✅ API Version: {info.get('version')}")
    print(f"✅ Layouts: {info.get('layouts')}")

    # Test get layouts
    layouts = client.get_layouts()
    print(f"✅ Total layouts: {layouts.get('total_layouts')}")

    print("\n🎉 Client working correctly!")
