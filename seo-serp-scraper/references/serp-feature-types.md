# SERP Feature Types

Reference guide for identifying and extracting different SERP features.

## Feature Types Overview

### 1. Organic Results
- **Description**: Standard 10 blue links ranked by relevance and authority
- **Signals**: Position 1–10, title + URL + snippet present
- **Extraction**: `type == "organic"` or no special type marker
- **Key fields**: position, title, url, snippet, sitelinks (optional)

### 2. Featured Snippet (Position Zero)
- **Description**: Boxed answer appearing above organic results
- **Signals**: Appears at position 0, often labeled "Featured snippet from the web"
- **Types**: Paragraph, list, table, video
- **Extraction**: `type == "featured_snippet"` or `position == 0`
- **Key fields**: text (extracted answer), url, title, format (paragraph|list|table)
- **Rule**: Snippet text is usually 40–60 words; look for complete sentence structure

### 3. People Also Ask (PAA)
- **Description**: Expandable question boxes related to the query
- **Signals**: Contains "?" in title/question, type == "paa" or "people_also_ask"
- **Extraction**: Detect questions ending in "?" in titles or snippet intro text
- **Key fields**: question, answer_snippet, url, source_domain
- **Rule**: Group all PAA items into a separate `paa[]` array

### 4. Knowledge Panel
- **Description**: Information box about entities (people, companies, places)
- **Signals**: `type == "knowledge_panel"`, appears on right side
- **Extraction**: Contains structured entity data (name, description, facts)
- **Key fields**: entity_name, description, attributes{}, image_url
- **Rule**: Skip if irrelevant to SEO competitive analysis

### 5. Video Carousel
- **Description**: Horizontal scroll of video thumbnails
- **Signals**: `type == "video"` or `type == "video_carousel"`
- **Extraction**: Extract video titles, URLs (youtube.com, vimeo.com), duration
- **Key fields**: title, url, platform, duration, thumbnail_url
- **Rule**: Note video dominance as a content-type signal for the query

### 6. Local Pack (Map Pack)
- **Description**: 3 local business listings with map
- **Signals**: `type == "local_pack"` or `type == "local_results"`
- **Extraction**: Business name, address, rating, hours
- **Key fields**: name, address, rating, reviews_count, phone
- **Rule**: Presence indicates local intent; pure SEO campaigns may skip

### 7. Image Pack
- **Description**: Row of image thumbnails in organic results
- **Signals**: `type == "image_pack"` or `type == "images"`
- **Extraction**: Image source URLs, alt text when available
- **Key fields**: image_urls[], source_domains[]
- **Rule**: Indicates visual search intent; recommend image optimization

### 8. Related Searches
- **Description**: Bottom-of-page suggestions from Google
- **Signals**: `type == "related_searches"` or at end of results
- **Extraction**: Extract as flat string array
- **Key fields**: query strings only

## Extraction Priority

When processing SERP data, apply this priority order:
1. Detect featured snippet first (position 0 or explicit type)
2. Group PAA items (question detection via "?" pattern)
3. Classify video/image/local packs by type field
4. Remaining results default to organic with position tracking
5. Extract related searches last (usually at end of result set)

## Regex Patterns for Detection

```python
# PAA detection
PAA_PATTERN = re.compile(r'.+\?$')

# Featured snippet markers
FEATURED_MARKERS = ['featured snippet', 'position 0', 'answer box']

# Question words for PAA fallback detection
QUESTION_STARTERS = ('what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'does', 'is', 'are')
```
