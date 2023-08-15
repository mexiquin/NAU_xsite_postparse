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
        results = executor.map(requests.get, [IN_DOT_NAU, NAU])

        for result in results:
            result.encoding = 'utf-8-sig'
            result = result.json()

            urls = urls + [site['url'] for site in result]


    return urls

def get_posts(endpoint: str) -> list:
    per_page = 15
    offset = 0
    json_collection = []

    while True:
        arg_str = "https://" + endpoint + "?per_page=" + str(per_page)  + (f"&offset={str(offset)}" if offset > 0 else '')
        import requests
        json_data = requests.get(arg_str)
        json_data.encoding = 'utf-8-sig'
        json_data = json_data.json()

        if len(json_data) > 0:
            json_collection = json_collection + [data['link'] for data in json_data]
            offset += per_page
        else:
            break

    return json_collection

def find_selector(url: str, selector: str) -> tuple:
    post, page = to_post_endpoint(url)
    posts = get_posts(post)
    pages = get_posts(page)

    all_posts: list[str] = posts + pages

    from bs4 import BeautifulSoup
    import requests

    for post in all_posts:
        
        # get html from post and check if selector is in html
        html = requests.get(post)
        html.encoding = 'utf-8-sig'
        html = html.text
        soup = BeautifulSoup(html, 'html.parser')

        selections = soup.select(selector)

        if selections:
            return (post, len(selections))


def main():

    # command line arguments to accept selector and optional output directory
    import argparse
    parser = argparse.ArgumentParser(description='Find selector in NAU sites')
    parser.add_argument('selector', type=str, help='CSS selector to find')
    parser.add_argument('-o', '--output', type=str, help='Output directory')
    args = parser.parse_args()

    selector = args.selector
    output = args.output

    sites = get_all_nau_sites()

    for site in sites:
        if output:
            with open(output, 'a') as f:
                f.write(f"{site}, {find_selector(site, selector)}\n")
        else:
            print(f"{site}, {find_selector(site, selector)}")

    print("Done...")


if __name__ == "__main__":
    main()