def to_post_endpoint(url) -> tuple:
    endpoints = ["wp-json/wp/v2/posts", "wp-json/wp/v2/pages"]

    # concatenate url with endpoint in URL format
    from urllib.parse import urljoin
    return (urljoin(url, endpoints[0]), urljoin(url, endpoints[1]))

def get_all_nau_sites() -> list:
    IN_DOT_NAU = "https://in.nau.edu/wp-json/enterprise/v1/site-list"
    NAU = "https://nau.edu/coe/wp-json/enterprise/v1/site-list"

    import requests
    in_sites = requests.get(IN_DOT_NAU)
    in_sites.encoding = 'utf-8-sig'
    in_sites = in_sites.json()

    nau_sites = requests.get(NAU)
    nau_sites.encoding = 'utf-8-sig'
    nau_sites = nau_sites.json()

    urls = [site['url'] for site in nau_sites] + [site['url'] for site in in_sites]

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
    selector = "section.nau-block-panels"

    sites = get_all_nau_sites()

    for site in sites:
        find_selector(site, selector)


if __name__ == "__main__":
    main()