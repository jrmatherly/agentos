#!/usr/bin/env bash
# =============================================================================
# Release Script
# =============================================================================
# Creates a new release by:
# 1. Auto-incrementing version (or accepting override)
# 2. Creating and pushing a git tag
# 3. Creating a GitHub release to trigger docker-images.yml workflow
#
# Usage:
#   ./scripts/release.sh           # Auto-increment patch version (interactive)
#   ./scripts/release.sh v1.2.3    # Use specific version
#   ./scripts/release.sh major     # Increment major version
#   ./scripts/release.sh minor     # Increment minor version
#   ./scripts/release.sh patch     # Increment patch version (default)
#   ./scripts/release.sh --yes     # Skip confirmation prompt
#   ./scripts/release.sh minor -y  # Combine version type with auto-confirm
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
YES_FLAG=false

# Get the latest tag, default to v0.0.0 if none exists
get_latest_tag() {
    git fetch --tags --quiet 2>/dev/null || true
    local latest
    latest=$(git tag -l 'v*' --sort=-v:refname | head -n1)
    echo "${latest:-v0.0.0}"
}

# Parse version into components
parse_version() {
    local version="${1#v}"  # Remove 'v' prefix
    IFS='.' read -r major minor patch <<< "$version"
    echo "$major $minor $patch"
}

# Increment version based on type
increment_version() {
    local current="$1"
    local type="${2:-patch}"

    read -r major minor patch <<< "$(parse_version "$current")"

    case "$type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch|*)
            patch=$((patch + 1))
            ;;
    esac

    echo "v${major}.${minor}.${patch}"
}

# Generate release notes from commits since last tag
generate_release_notes() {
    local last_tag="$1"
    local notes=""

    # Get commits since last tag (or all commits if no tag)
    if git rev-parse "$last_tag" >/dev/null 2>&1; then
        notes=$(git log "${last_tag}..HEAD" --pretty=format:"- %s" --no-merges 2>/dev/null || echo "")
    else
        notes=$(git log --pretty=format:"- %s" --no-merges -20 2>/dev/null || echo "")
    fi

    if [[ -z "$notes" ]]; then
        notes="- Initial release"
    fi

    echo "$notes"
}

# Main
main() {
    local input=""
    local latest_tag
    local new_version

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -y|--yes)
                YES_FLAG=true
                shift
                ;;
            *)
                input="$1"
                shift
                ;;
        esac
    done

    # Ensure we're in a git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}Error: Not a git repository${NC}"
        exit 1
    fi

    # Ensure working directory is clean
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${RED}Error: Working directory is not clean. Commit or stash changes first.${NC}"
        exit 1
    fi

    # Ensure gh CLI is authenticated
    if ! gh auth status >/dev/null 2>&1; then
        echo -e "${RED}Error: gh CLI not authenticated. Run 'gh auth login' first.${NC}"
        exit 1
    fi

    latest_tag=$(get_latest_tag)
    echo -e "${BLUE}Current version:${NC} $latest_tag"

    # Determine new version
    if [[ -z "$input" ]]; then
        # Interactive mode - prompt for version type
        new_version=$(increment_version "$latest_tag" "patch")
        echo -e "${YELLOW}Next version will be:${NC} $new_version"
        echo ""
        echo "Options:"
        echo "  [Enter] Accept $new_version (patch increment)"
        echo "  major   Increment major version"
        echo "  minor   Increment minor version"
        echo "  vX.Y.Z  Specify exact version"
        echo "  q       Quit"
        echo ""
        read -rp "Your choice: " choice

        case "$choice" in
            "")
                # Accept default
                ;;
            major)
                new_version=$(increment_version "$latest_tag" "major")
                ;;
            minor)
                new_version=$(increment_version "$latest_tag" "minor")
                ;;
            q|Q)
                echo "Aborted."
                exit 0
                ;;
            v*)
                new_version="$choice"
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                exit 1
                ;;
        esac
    elif [[ "$input" == "major" || "$input" == "minor" || "$input" == "patch" ]]; then
        new_version=$(increment_version "$latest_tag" "$input")
    elif [[ "$input" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        # Ensure 'v' prefix
        new_version="v${input#v}"
    else
        echo -e "${RED}Invalid version format: $input${NC}"
        echo "Use: vX.Y.Z, major, minor, or patch"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}Creating release:${NC} $new_version"
    echo ""

    # Generate release notes
    local release_notes
    release_notes=$(generate_release_notes "$latest_tag")

    echo -e "${BLUE}Release notes:${NC}"
    echo "$release_notes"
    echo ""

    # Confirm (skip if --yes flag provided)
    if [[ "$YES_FLAG" != true ]]; then
        read -rp "Proceed with release? [y/N] " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 0
        fi
    fi

    # Create and push tag
    echo ""
    echo -e "${BLUE}Creating tag...${NC}"
    git tag -a "$new_version" -m "Release $new_version"

    echo -e "${BLUE}Pushing tag...${NC}"
    git push origin "$new_version"

    # Create GitHub release
    echo -e "${BLUE}Creating GitHub release...${NC}"
    gh release create "$new_version" \
        --title "$new_version" \
        --notes "$release_notes" \
        --latest

    echo ""
    echo -e "${GREEN}✓ Release $new_version created successfully!${NC}"
    echo ""
    echo "The docker-images.yml workflow should now be triggered."
    echo "View releases: gh release list"
    echo "View workflow: gh run list --workflow=docker-images.yml"
}

main "$@"
