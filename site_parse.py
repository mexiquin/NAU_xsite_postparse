def to_post_endpoint(url) -> tuple:
    endpoints = ["wp-json/wp/v2/posts", "wp-json/wp/v2/pages"]

    # concatenate url with endpoint in URL format
    from urllib.parse import urljoin
    return (urljoin(url, endpoints[0]), urljoin(url, endpoints[1]))

def get_all_nau_sites(login) -> list:
    IN_DOT_NAU = "https://in.nau.edu/wp-json/enterprise/v1/sites-by-theme/nau-marketing-2021"
    NAU = "https://nau.edu/coe/wp-json/enterprise/v1/sites-by-theme/nau-marketing-2021"

    urls = []

    import requests
    import concurrent.futures as cf

    with cf.ThreadPoolExecutor() as executor:
        def worker(param):
            try:
                return requests.get(param, auth=login)
            except:
                return None
        results = executor.map(worker, [NAU, IN_DOT_NAU])

        for result in results:
            result.encoding = 'utf-8-sig'
            result = result.json()

            urls = urls + [site['url'] for site in result]


    return urls

def get_posts(endpoint: str) -> list:
    json_collection = []
    potential_pages = gen_pagination_urls(endpoint)
    def serialize(response):
        try:
            response.encoding = 'utf-8-sig'
            return response.json()
        except:
            pass

    import concurrent.futures as cf
    import requests
    with cf.ThreadPoolExecutor() as executor:
        def worker(param):
            try:
                return requests.get(param)
            except:
                return None
            
        results = executor.map(worker, potential_pages)

    results = [result for result in map(serialize, results)]

    for result in results:
        if result:
            json_collection = json_collection + [post['link'] for post in result]


    if result and len(result) > 0:
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

        matches = executor.map(search_selector, all_posts, [selector] * (len(all_posts) if all_posts else 1))
        matches = [match for match in matches if match[1] > 0]

    return matches


def gen_pagination_urls(endpoint_url: str, max=20) -> list:
    per_page = 15
    max_pagination = per_page * max
    urls = ["https://" + endpoint_url + "?per_page=" + str(per_page)  + (f"&offset={str(offset)}" if offset > 0 else '') for offset in range(0, max_pagination+1, per_page)]
    return urls

def main():
    
    import argparse
    import sys
    description = "Find block by selector in NAU sites.\n\
    You can use this to print out all marketing-2021 sites that contain a specific selector.\n\
    Or you can pipe the STDOUT to a file to save the results for later.\n\
    Data is sent to STDOUT. All progress is printed to STDERR.\n\
    Output data will be in TSV format:\n\
    page/post-url (tab) number-of-blocks-present\n"
    
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('selector', type=str, help='CSS selector to find')
    parser.add_argument('-u','--username', type=str, help='Username for NAU sites', default='')
    parser.add_argument('-p','--password', type=str, help='Password for NAU sites', default='')
    args = parser.parse_args()

    selector = args.selector
    login = (args.username, args.password)

    try:

        sites = get_all_nau_sites(login)
        sys.stderr.write("[INFO] Found " + str(len(sites)) + " sites\n")

        for iter, site in enumerate(sites):
            sys.stderr.write("[INFO] Processing site " + str(iter) + " of " + str(len(sites)) + f" ({site})\n")
            matches = find_selector(site, selector)
            for item in matches:
                sys.stdout.write("Page: " + item[0] + "\tNum Blocks: " + str(item[1]) + "\n")

        sys.stderr.write("[INFO] Process Complete...\n")

    except KeyboardInterrupt:
        sys.stderr.write("[ERROR] Process Interrupted...\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
