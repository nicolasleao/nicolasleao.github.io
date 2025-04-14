#!/usr/bin/env python3
import os
import re
import json
import datetime
import markdown
import argparse
from bs4 import BeautifulSoup
from pathlib import Path

def load_post_data():
    """Load the post-data.json file or create it if it doesn't exist"""
    data_file = Path('post-data.json')
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Create default post_data file
        post_data = {
            "version": "1.0.0",
            "posts": []
        }
        save_post_data(post_data)
        return post_data

def save_post_data(post_data):
    """Save the post_data data to post-data.json"""
    with open('post-data.json', 'w', encoding='utf-8') as f:
        json.dump(post_data, f, indent=2)

def update_app_version(new_version):
    """Update the app version in post-data.json"""
    post_data = load_post_data()
    current_version = post_data["version"]
    
    if current_version != new_version:
        print(f"Updating app version from {current_version} to {new_version}")
        post_data["version"] = new_version
        save_post_data(post_data)
        return True
    else:
        print(f"App version is already at {current_version}")
        return False

def get_files_to_convert(force=False):
    """
    Get a list of markdown files in src/ that don't have HTML counterparts in posts/
    or need to be updated due to template version changes
    Returns a list of tuples: (md_file_path, html_file_path, is_update)
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
    
    # Load post_data data
    post_data_obj = load_post_data()
    current_version = post_data_obj["version"]
    
    # Find markdown files without HTML counterparts or requiring updates
    files_to_convert = []
    for md_file in md_files:
        html_file = posts_dir / f"{md_file.stem}.html"
        is_update = False
        
        # Check if this is a new file or an existing one that needs update
        if md_file.stem not in html_filenames:
            # New file
            files_to_convert.append((md_file, html_file, is_update))
        else:
            # If force is true, add all files
            if force:
                is_update = True
                files_to_convert.append((md_file, html_file, is_update))
            else:
                # Check if the post version is different from the current version
                post_entry = next((p for p in post_data_obj["posts"] if p["slug"] == md_file.stem), None)
                if post_entry and post_entry["version"] != current_version:
                    is_update = True
                    files_to_convert.append((md_file, html_file, is_update))
    
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

def render_markdown_to_html(md_file, html_file, is_update=False):
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
    
    # If it's an update, we need to preserve the original date
    if is_update:
        post_data_obj = load_post_data()
        post_entry = next((p for p in post_data_obj["posts"] if p["slug"] == md_file.stem), None)
        if post_entry and "created_at" in post_entry:
            # Convert from ISO format (YYYY-MM-DD) to display format (MMM DD, YYYY)
            date_obj = datetime.datetime.strptime(post_entry["created_at"], "%Y-%m-%d")
            today = date_obj.strftime("%b %d, %Y")
    
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
    
    # Update post_data information
    update_post_data(md_file.stem, title, is_update)
    
    return title, today

def update_post_data(slug, title, is_update):
    """Update the post-data.json file with the new or updated post"""
    post_data_obj = load_post_data()
    current_version = post_data_obj["version"]
    today_iso = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Check if the post already exists in post_data
    post_index = next((i for i, p in enumerate(post_data_obj["posts"]) 
                      if p["slug"] == slug), None)
    
    if post_index is not None:
        # Update existing post
        post_data_obj["posts"][post_index]["version"] = current_version
        if not is_update:
            # Only update created_at if it's not an update to preserve original date
            post_data_obj["posts"][post_index]["created_at"] = today_iso
    else:
        # Add new post
        post_data_obj["posts"].append({
            "slug": slug,
            "version": current_version,
            "created_at": today_iso
        })
    
    # Save the updated post_data
    save_post_data(post_data_obj)

def update_index_html(new_posts):
    """Update index.html with links to new posts"""
    if not new_posts:
        return
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    post_list = soup.select_one('.post-list')
    
    # Load post_data for date information
    post_data_obj = load_post_data()
    
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
    parser = argparse.ArgumentParser(description='Blog post processor and post_data tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build markdown files into HTML')
    build_parser.add_argument('--force', '-f', action='store_true', help='Force rebuild all posts')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Update app version')
    version_parser.add_argument('new_version', help='New version number (e.g., 1.0.1)')
    
    # Regenerate command
    regen_parser = subparsers.add_parser('regenerate', help='Regenerate all posts using current template')
    
    args = parser.parse_args()
    
    # Handle version update command
    if args.command == 'version':
        updated = update_app_version(args.new_version)
        if updated:
            print("Version updated successfully. Run 'build' to update posts with the new version.")
        return
    
    # Handle regenerate command
    if args.command == 'regenerate':
        regenerate_all_posts()
        return
    
    # Default to build if no command specified
    if not args.command or args.command == 'build':
        force = getattr(args, 'force', False)
        process_markdown_files(force)

def regenerate_all_posts():
    """Force regenerate all posts using the current template"""
    # Get all markdown files
    src_dir = Path('src')
    posts_dir = Path('posts')
    
    # Make sure directories exist
    posts_dir.mkdir(exist_ok=True)
    src_dir.mkdir(exist_ok=True)
    
    # Get all markdown files in src
    md_files = list(src_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found to regenerate")
        return
    
    print(f"Regenerating {len(md_files)} posts...")
    
    # Process each file
    for md_file in md_files:
        html_file = posts_dir / f"{md_file.stem}.html"
        print(f"Regenerating {html_file}...")
        title, date = render_markdown_to_html(md_file, html_file, is_update=True)
        print(f"Updated {html_file}")
    
    print("Done!")

def process_markdown_files(force=False):
    """Process markdown files and update the index"""
    files_to_convert = get_files_to_convert(force)
    
    if not files_to_convert:
        print("No new markdown files to convert or posts to update")
        return
    
    print(f"Found {len(files_to_convert)} markdown files to process:")
    
    new_posts = []
    for md_file, html_file, is_update in files_to_convert:
        action = "Updating" if is_update else "Converting"
        print(f"{action} {md_file} to {html_file}...")
        title, date = render_markdown_to_html(md_file, html_file, is_update)
        
        if not is_update:
            # Only add to index if it's a new post, not an update
            new_posts.append((html_file, title, date))
        
        print(f"{'Updated' if is_update else 'Created'} {html_file}")
    
    if new_posts:
        print("Updating index.html...")
        update_index_html(new_posts)
    
    print("Done!")

if __name__ == "__main__":
    main() 