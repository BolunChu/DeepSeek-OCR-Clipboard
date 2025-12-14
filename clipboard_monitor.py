from PIL import ImageGrab, Image
import io
import hashlib

class ClipboardMonitor:
    def __init__(self):
        self.last_image_hash = None

    def _get_image_hash(self, image):
        """Generates a hash for the image to detect changes."""
        # Resize to small size for faster hashing, or just hash bytes
        # Hashing raw bytes of a newly grabbed image might differ if metadata changes
        # But for clipboard grab, usually consistent.
        try:
            with io.BytesIO() as out:
                image.save(out, format="PNG")
                return hashlib.md5(out.getvalue()).hexdigest()
        except Exception:
            return None

    def check(self):
        """
        Checks the clipboard for a new image.
        Returns the PIL Image if a new image is found, otherwise None.
        """
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                current_hash = self._get_image_hash(image)
                if current_hash and current_hash != self.last_image_hash:
                    self.last_image_hash = current_hash
                    return image
        except Exception as e:
            print(f"Clipboard check error: {e}")
        
        return None
