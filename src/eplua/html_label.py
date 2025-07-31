"""
Simple HTML rendering for tkinter labels
Supports basic HTML tags like <b>, <i>, <font>, <br>, etc.
"""

import tkinter as tk
import re
from typing import Dict, List, Tuple, Any


class SimpleHTMLLabel:
    """A tkinter widget that can render simple HTML in labels"""
    
    def __init__(self, parent, html_text="", **kwargs):
        self.parent = parent
        self.html_text = html_text
        self.kwargs = kwargs
        
        # Create a Text widget for rich formatting (read-only)
        self.text_widget = tk.Text(parent, wrap=tk.WORD, state=tk.DISABLED, 
                                  cursor="arrow", **kwargs)
        
        # Configure text widget to look like a label
        self.text_widget.configure(
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else 'white'
        )
        
        self.render_html(html_text)
    
    def render_html(self, html_text: str):
        """Render HTML text in the widget"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        # Parse and render HTML
        self._parse_and_render(html_text)
        
        self.text_widget.config(state=tk.DISABLED)
    
    def _parse_and_render(self, html_text: str):
        """Parse HTML and apply formatting"""
        # Simple HTML parser for basic tags
        
        # Define tag mappings to tkinter text tags
        tag_configs = {
            'bold': {'font': ('TkDefaultFont', 10, 'bold')},
            'italic': {'font': ('TkDefaultFont', 10, 'italic')},
            'underline': {'underline': True},
            'large': {'font': ('TkDefaultFont', 14)},
            'small': {'font': ('TkDefaultFont', 8)},
            'red': {'foreground': 'red'},
            'blue': {'foreground': 'blue'},
            'green': {'foreground': 'green'},
        }
        
        # Configure text tags
        for tag_name, config in tag_configs.items():
            self.text_widget.tag_configure(tag_name, **config)
        
        # Current position and active tags
        pos = 0
        tag_stack = []
        
        # Simple regex patterns for HTML tags
        patterns = [
            (r'<b\b[^>]*>', 'bold', 'open'),
            (r'</b>', 'bold', 'close'),
            (r'<i\b[^>]*>', 'italic', 'open'),
            (r'</i>', 'italic', 'close'),
            (r'<u\b[^>]*>', 'underline', 'open'),
            (r'</u>', 'underline', 'close'),
            (r'<strong\b[^>]*>', 'bold', 'open'),
            (r'</strong>', 'bold', 'close'),
            (r'<em\b[^>]*>', 'italic', 'open'),
            (r'</em>', 'italic', 'close'),
            (r'<big\b[^>]*>', 'large', 'open'),
            (r'</big>', 'large', 'close'),
            (r'<small\b[^>]*>', 'small', 'open'),
            (r'</small>', 'small', 'close'),
            (r'<br\s*/?>', 'newline', 'single'),
            (r'<font[^>]*color\s*=\s*["\']?red["\']?[^>]*>', 'red', 'open'),
            (r'<font[^>]*color\s*=\s*["\']?blue["\']?[^>]*>', 'blue', 'open'),
            (r'<font[^>]*color\s*=\s*["\']?green["\']?[^>]*>', 'green', 'open'),
            (r'</font>', 'font_close', 'close'),
        ]
        
        # Find all matches
        matches = []
        for pattern, tag, action in patterns:
            for match in re.finditer(pattern, html_text, re.IGNORECASE):
                matches.append((match.start(), match.end(), tag, action))
        
        # Sort matches by position
        matches.sort()
        
        # Process text with tags
        last_pos = 0
        for start, end, tag, action in matches:
            # Insert text before the tag
            if start > last_pos:
                text = html_text[last_pos:start]
                self._insert_text(text, tag_stack[:])
            
            # Handle the tag
            if action == 'open':
                tag_stack.append(tag)
            elif action == 'close':
                if tag == 'font_close':
                    # Close any font color tag
                    tag_stack = [t for t in tag_stack if t not in ['red', 'blue', 'green']]
                else:
                    # Remove the specific tag
                    if tag in tag_stack:
                        tag_stack.remove(tag)
            elif action == 'single':
                if tag == 'newline':
                    self.text_widget.insert(tk.END, '\n')
            
            last_pos = end
        
        # Insert remaining text
        if last_pos < len(html_text):
            text = html_text[last_pos:]
            self._insert_text(text, tag_stack[:])
    
    def _insert_text(self, text: str, active_tags: List[str]):
        """Insert text with the given tags"""
        if not text.strip() and '\n' not in text:
            return
        
        start_pos = self.text_widget.index(tk.END + '-1c')
        self.text_widget.insert(tk.END, text)
        end_pos = self.text_widget.index(tk.END + '-1c')
        
        # Apply all active tags
        for tag in active_tags:
            self.text_widget.tag_add(tag, start_pos, end_pos)
    
    def pack(self, **kwargs):
        """Pack the widget"""
        return self.text_widget.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        return self.text_widget.grid(**kwargs)
    
    def configure(self, **kwargs):
        """Configure the widget"""
        return self.text_widget.configure(**kwargs)
    
    def config(self, **kwargs):
        """Configure the widget (alias)"""
        return self.configure(**kwargs)


def create_html_label(parent, html_text="", **kwargs):
    """Convenience function to create an HTML label"""
    return SimpleHTMLLabel(parent, html_text, **kwargs)


# Test function
if __name__ == "__main__":
    root = tk.Tk()
    root.title("HTML Label Test")
    
    test_html = """
    <b>Bold text</b> and <i>italic text</i><br>
    <font color="red">Red text</font> and <font color="blue">blue text</font><br>
    <big>Large text</big> and <small>small text</small><br>
    <u>Underlined text</u> and <strong>strong text</strong><br>
    Normal text with <em>emphasis</em>
    """
    
    label = create_html_label(root, test_html, width=50, height=10)
    label.pack(padx=20, pady=20)
    
    root.mainloop()
