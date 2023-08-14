def to_post_endpoint(url) -> tuple(str, str):
    endpoints = ["wp-json/wp/v2/posts", "wp-json/wp/v2/pages"]

    # concatenate url with endpoint in URL format
    from urllib.parse import urljoin
    return (urljoin(url, endpoints[0]), urljoin(url, endpoints[1]))

def get_all_nau_sites() -> list:
    IN_DOT_NAU = "https://in.nau.edu/wp-json/enterprise/v1/site-list"
    NAU = "https://nau.edu/coe/wp-json/enterprise/v1/site-list"

    import requests
    return requests.get(IN_DOT_NAU).json()['url'] + requests.get(NAU).json()['url']

def get_posts(endpoint: str) -> list:
    per_page = 15
    offset = 0
    json_collection = []

    while True:
        arg_str = endpoint + "?per_page=" + str(per_page) + "&offset=" + str(offset) if offset > 0 else ""
        import requests
        json = requests.get(arg_str).json()
        if len(json) > 0:
            json_collection.append(json)
            offset += per_page
        else:
            break

    return json_collection

def find_selector(url: str, selector: str) -> tuple(str, int):
    post, page = to_post_endpoint(url)
    posts = get_posts(post)
    pages = get_posts(page)

    all_posts: list[str] = posts + pages

    from bs4 import BeautifulSoup
    import requests

    for post in all_posts:
        pass




def main():
    selector = "section.nau-block-panels"

    sites = get_all_nau_sites()

    for site in sites:
        find_selector(site, selector)


if __name__ == "__main__":
    main()