from pathlib import Path

def load_css():
    """
    Load and return the global CSS stylesheet wrapped in <style> tags.
    The CSS file is located at assets/style.css relative to the streamlit_app directory.
    """
    # Get the directory where this helper file is located
    utils_dir = Path(__file__).parent
    # Go up one level to streamlit_app, then to assets
    css_path = utils_dir.parent / "assets" / "style.css"
    
    try:
        with open(css_path, "r", encoding="utf-8") as css_file:
            css_content = css_file.read()
        return f"<style>{css_content}</style>"
    except FileNotFoundError:
        # Fallback: try relative path from current working directory
        fallback_path = Path("assets/style.css")
        if fallback_path.exists():
            with open(fallback_path, "r", encoding="utf-8") as css_file:
                css_content = css_file.read()
            return f"<style>{css_content}</style>"
        return "<style></style>"  # Return empty style tag if file not found

