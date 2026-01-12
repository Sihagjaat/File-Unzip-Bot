import os
import re


def parse_replacement_rules(rules_string):
    """
    Parse pipe-separated replacement rules
    
    Args:
        rules_string (str): Pipe-separated rules like "old:new | old2:new2 | remove_word"
    
    Returns:
        list: List of rule dicts with 'old'/'new' or 'remove' keys
    """
    if not rules_string or not rules_string.strip():
        return []
    
    rules = []
    parts = [part.strip() for part in rules_string.split('|')]
    
    for part in parts:
        if not part:
            continue
            
        if ':' in part:
            # Replacement rule
            old, new = part.split(':', 1)
            rules.append({"old": old.strip(), "new": new.strip()})
        else:
            # Removal rule
            rules.append({"remove": part.strip()})
    
    return rules


def apply_replacements(text, rules_string):
    """
    Apply word replacements and removals to text
    
    Args:
        text (str): Text to transform
        rules_string (str): Pipe-separated rules
    
    Returns:
        str: Transformed text
    """
    if not text or not rules_string:
        return text
    
    rules = parse_replacement_rules(rules_string)
    result = text
    
    for rule in rules:
        if "remove" in rule:
            # Remove all occurrences
            result = result.replace(rule["remove"], "")
        else:
            # Replace old with new
            result = result.replace(rule["old"], rule["new"])
    
    return result


def add_prefix_suffix(filename, prefix, suffix):
    """
    Add prefix and suffix to filename with space separation
    
    Args:
        filename (str): Original filename
        prefix (str or None): Prefix to add (space added automatically)
        suffix (str or None): Suffix to add (space added automatically, before extension)
    
    Returns:
        str: Transformed filename
    
    Example:
        add_prefix_suffix("file.pdf", "[VIP]", "HD") -> "[VIP] file HD.pdf"
    """
    # Split filename and extension
    name, ext = os.path.splitext(filename)
    
    # Add prefix with space
    if prefix:
        # Avoid double spaces if prefix already ends with space
        if prefix.endswith(' '):
            name = prefix + name
        else:
            name = prefix + ' ' + name
    
    # Add suffix with space
    if suffix:
        # Avoid double spaces if suffix already starts with space
        if suffix.startswith(' '):
            name = name + suffix
        else:
            name = name + ' ' + suffix
    
    # Combine name and extension
    return name + ext


def transform_filename(filename, settings):
    """
    Apply all filename transformations in correct order
    
    Order:
    1. Apply filename replacements
    2. Add prefix
    3. Add suffix
    
    Args:
        filename (str): Original filename
        settings (dict): User settings dict
    
    Returns:
        str: Fully transformed filename
    """
    result = filename
    
    # Step 1: Apply replacements/removals
    if settings.get('filename_replacements'):
        result = apply_replacements(result, settings['filename_replacements'])
    
    # Step 2 & 3: Add prefix and suffix
    result = add_prefix_suffix(
        result,
        settings.get('filename_prefix'),
        settings.get('filename_suffix')
    )
    
    return result


def substitute_caption_variables(template, file_info):
    """
    Replace variables in caption template with actual values
    
    Args:
        template (str): Caption template with variables
        file_info (dict): Dict with 'filename', 'size', 'extension', 'caption' keys
    
    Returns:
        str: Caption with variables replaced
    
    Variables:
        {filename} - File name (after all transformations)
        {size} - File size in human-readable format
        {extension} - File extension without dot
        {caption} - Original caption if any
    """
    if not template:
        return None
    
    result = template
    
    # Replace each variable
    result = result.replace('{filename}', file_info.get('filename', ''))
    result = result.replace('{size}', file_info.get('size', ''))
    result = result.replace('{extension}', file_info.get('extension', ''))
    result = result.replace('{caption}', file_info.get('caption', ''))
    
    return result


def get_file_type(filename):
    """
    Determine file type based on extension
    
    Args:
        filename (str): File name
    
    Returns:
        str: 'photo', 'video', or 'document'
    """
    ext = os.path.splitext(filename)[1].lower()
    
    photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    
    if ext in photo_extensions:
        return 'photo'
    elif ext in video_extensions:
        return 'video'
    else:
        return 'document'
