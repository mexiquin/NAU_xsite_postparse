def to_post_endpoint(url) -> tuple:
    endpoints = ["wp-json/wp/v2/posts", "wp-json/wp/v2/pages"]

    # concatenate url with endpoint in URL format
    from urllib.parse import urljoin
    return (urljoin(url, endpoints[0]), urljoin(url, endpoints[1]))

def get_all_nau_sites() -> list:
    IN_DOT_NAU = "https://in.nau.edu/wp-json/enterprise/v1/site-list"
    NAU = "https://nau.edu/coe/wp-json/enterprise/v1/site-list"

    urls = []

    import requests
    import concurrent.futures as cf

    with cf.ThreadPoolExecutor() as executor:
        results = executor.map(requests.get, [NAU, IN_DOT_NAU])

        for result in results:
            result.encoding = 'utf-8-sig'
            result = result.json()

            urls = urls + [site['url'] for site in result]


    return urls

def get_posts(endpoint: str) -> list:
    json_collection = []
    potential_pages = gen_pagination_urls(endpoint)
    def serialize(response):
        response.encoding = 'utf-8-sig'
        return response.json()

    import concurrent.futures as cf
    import requests
    with cf.ThreadPoolExecutor() as executor:
        results = executor.map(requests.get, potential_pages)

    executor.shutdown(wait=True)

    results = [result for result in map(serialize, results)]

    for result in results:
        if result:
            json_collection = json_collection + [post['link'] for post in result]


    if len(result) > 0:
        json_collection = json_collection + [post['link'] for post in result]

    return json_collection

def find_selector(url: str, selector: str) -> tuple:
    from bs4 import BeautifulSoup
    import concurrent.futures as cf
    import requests
    def search_selector(post: str, selector: str) -> tuple:
        try:
            html = requests.get(post)
            html.encoding = 'utf-8-sig'
            html = html.text
            soup = BeautifulSoup(html, 'html.parser')

            selections = soup.select(selector)

            if selections:
                return (post, len(selections))
        except:
            pass

        return (post, 0)

    post, page = to_post_endpoint(url)

    import concurrent.futures as cf

    with cf.ThreadPoolExecutor() as executor:
        results = executor.map(get_posts, [post, page])
        all_posts = [link for grouping in results for link in grouping]

        matches = executor.map(search_selector, all_posts, [selector] * len(all_posts))
        matches = [match for match in matches if match[1] > 0]

    return matches


def gen_pagination_urls(endpoint_url: str) -> list:
    per_page = 15
    max_pagination = per_page * 50
    urls = ["https://" + endpoint_url + "?per_page=" + str(per_page)  + (f"&offset={str(offset)}" if offset > 0 else '') for offset in range(0, max_pagination+1, per_page)]
    return urls

def main():

    # command line arguments to accept selector and optional output directory
    import argparse
    parser = argparse.ArgumentParser(description='Find selector in NAU sites')
    parser.add_argument('selector', type=str, help='CSS selector to find')
    parser.add_argument('-o', '--output', type=str, help='Output directory')
    parser.add_argument('-e', '--exclude', nargs='+', help='List of sites to exclude', default='')


    
    args = parser.parse_args()

    selector = args.selector
    output = args.output

    sites = get_all_nau_sites()

    import pandas as pd

    df = []

    for site in sites:
        if args.exclude not in site:
            matches = find_selector(site, selector)
            for item in matches:
                print("Page: " + item[0], "Num Blocks: " + str(item[1]))
            df.append({site: matches})

    print("Done...")


if __name__ == "__main__":
    main()