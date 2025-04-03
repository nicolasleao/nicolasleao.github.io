#!/usr/bin/env python3
import os
import re
import datetime
import markdown
from bs4 import BeautifulSoup
from pathlib import Path

def get_files_to_convert():
    """
    Get a list of markdown files in src/ that don't have HTML counterparts in posts/
    Returns a list of tuples: (md_file_path, html_file_path)
    """
    src_dir = Path('src')
    posts_dir = Path('posts')
    
    # Make sure directories exist
    posts_dir.mkdir(exist_ok=True)
    src_dir.mkdir(exist_ok=True)
    
    # Get all markdown files in src
    md_files = list(src_dir.glob('*.md'))
    
    # Get all html files in posts
    html_files = list(posts_dir.glob('*.html'))
    html_filenames = [f.stem for f in html_files]
    
    # Find markdown files without HTML counterparts
    files_to_convert = []
    for md_file in md_files:
        html_file = posts_dir / f"{md_file.stem}.html"
        if md_file.stem not in html_filenames:
            files_to_convert.append((md_file, html_file))
    
    return files_to_convert

def extract_title_from_markdown(md_content):
    """Extract title from markdown content (first heading)"""
    # Look for the first heading (# Title)
    match = re.search(r'^#\s+(.+?)$', md_content, re.MULTILINE)
    if match:
        return match.group(1)
    
    # If no heading found, use the first line
    first_line = md_content.strip().split('\n')[0]
    return first_line[:50]  # Limit to 50 chars

def process_content_for_output(soup):
    """
    Process the soup content to add target="_blank" to all external links
    and other modifications
    """
    # Add target="_blank" to all external links
    for a_tag in soup.find_all('a'):
        # Check if it's an external link (starts with http)
        if a_tag.get('href', '').startswith(('http://', 'https://')):
            a_tag['target'] = '_blank'
            # For security, add rel="noopener noreferrer"
            a_tag['rel'] = 'noopener noreferrer'
    
    return soup

def render_markdown_to_html(md_file, html_file):
    """Convert a markdown file to HTML and save it"""
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title
    title = extract_title_from_markdown(md_content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',  # Tables, footnotes, etc.
        'markdown.extensions.codehilite',  # Code highlighting
        'markdown.extensions.fenced_code',  # Fenced code blocks
        'markdown.extensions.toc'  # Table of contents
    ])
    content_html = md.convert(md_content)
    
    # Generate the full HTML
    today = datetime.datetime.now().strftime("%b %d, %Y")
    
    # Create the HTML template based on the _template.html format
    with open('posts/_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace the relevant parts of the template
    soup = BeautifulSoup(template, 'html.parser')
    
    # Update the title
    soup.title.string = f"{title} - Nicolas Leao"
    
    # Update the post title and date
    soup.select_one('.post-title').string = title
    soup.select_one('.post-date').string = today
    
    # Update the post content
    soup.select_one('.post-content').clear()
    content_soup = BeautifulSoup(content_html, 'html.parser')
    
    # Process the content (add target="_blank" to links, etc.)
    content_soup = process_content_for_output(content_soup)
    
    soup.select_one('.post-content').append(content_soup)
    
    # Write the HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return title, today

def update_index_html(new_posts):
    """Update index.html with links to new posts"""
    if not new_posts:
        return
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    post_list = soup.select_one('.post-list')
    
    # Add new posts to the list (newest first)
    for html_file, title, date in reversed(new_posts):
        # Create a new list item
        li = soup.new_tag('li', **{'class': 'post-item'})
        
        # Create link to the post
        relative_path = os.path.relpath(html_file, os.path.dirname('index.html'))
        a = soup.new_tag('a', href=relative_path, **{'class': 'post-title', 'target': '_blank'})
        a.string = title
        
        # Create date span
        span = soup.new_tag('span', **{'class': 'post-date'})
        span.string = date
        
        # Add the elements to the list item
        li.append(a)
        li.append(span)
        
        # Add the new post at the beginning of the list
        if post_list.find('li'):
            post_list.insert(0, li)
        else:
            post_list.append(li)
    
    # Write the updated index file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

def main():
    """Main function to process markdown files and update the index"""
    files_to_convert = get_files_to_convert()
    
    if not files_to_convert:
        print("No new markdown files to convert")
        return
    
    print(f"Found {len(files_to_convert)} markdown files to convert:")
    
    new_posts = []
    for md_file, html_file in files_to_convert:
        print(f"Converting {md_file} to {html_file}...")
        title, date = render_markdown_to_html(md_file, html_file)
        new_posts.append((html_file, title, date))
        print(f"Created {html_file}")
    
    print("Updating index.html...")
    update_index_html(new_posts)
    
    print("Done!")

if __name__ == "__main__":
    main() 