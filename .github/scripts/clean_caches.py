#!/usr/bin/env python3
import os
from collections import defaultdict
from github import Github

keep_count = 3

def main():
    token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('GITHUB_REPOSITORY')
    
    if not token or not repo_name:
        raise ValueError("GITHUB_TOKEN and GITHUB_REPOSITORY must be set")
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    caches = list(repo.get_actions_caches())
    
    if not caches:
        print("No caches found")
        return
    
    cache_groups = defaultdict(list)
    
    for cache in caches:
        key_parts = cache.key.split('-')
        base_key = '-'.join(key_parts[:-1]) + '-'
        cache_groups[base_key].append(cache)
    
    total_deleted = 0
    
    for base_key, group_caches in sorted(cache_groups.items()):
        sorted_caches = sorted(
            group_caches,
            key=lambda c: c.created_at,
            reverse=True
        )
        
        to_delete = sorted_caches[keep_count:]
        
        print(f"\nGroup: {base_key}")
        print(f"  Total: {len(sorted_caches)}, "
              f"Keeping: {min(keep_count, len(sorted_caches))}, "
              f"Deleting: {len(to_delete)}")
        
        for cache in to_delete:
            try:
                cache.delete()
                size_mb = cache.size_in_bytes / 1024 / 1024
                print(f"  ✓ Deleted: {cache.key} ({size_mb:.2f} MB)")
                total_deleted += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {cache.key}: {e}")
    
    print(f"\n✅ Cleanup completed. Deleted {total_deleted} caches")

if __name__ == '__main__':
    main()