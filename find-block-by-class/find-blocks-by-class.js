const { JSDOM } = require('jsdom');
const { window } = new JSDOM(``, { silent: true });
const jQuery = require( "jquery" )( window );
const fs = require('fs');

function to_post_endpoint(site) {
  return [
    "https://" + site + "wp-json/wp/v2/posts",
    "https://" + site + "wp-json/wp/v2/pages",
  ];
}

async function get_all_NAU_sites() {
  const IN_DOT_NAU = "https://in.nau.edu/wp-json/enterprise/v1/site-list";
  const NAU = "https://nau.edu/coe/wp-json/enterprise/v1/site-list";

  var nau_promise = jQuery.get(NAU);
  var in_nau_promise = jQuery.get(IN_DOT_NAU);

  let all_sites = await Promise.all([nau_promise, in_nau_promise]).then(
    (values) => {
      var nau_sites = values[0];
      var in_nau_sites = values[1];
      return nau_sites.concat(in_nau_sites);
    }
  ).catch((error) => {
    console.log(error)
  });

  return all_sites;
}

async function get_posts(endpoint) {
  const per_page = 15;

  var offset = 0;
  var json_array = [];

  do {
    var arg_str =
      endpoint +
      `?per_page=${per_page}` +
      (offset > 0 ? `&offset=${offset}` : "");

    var json_data = await jQuery
      .get(arg_str).then((data) => {
        return data;
      }).catch((error) => {
        console.log(error);
      });

    if (json_data !== undefined && json_data.length > 0) {
      json_array.push(json_data);
    }

    offset += per_page;
  } while (json_data !== undefined && Object.keys(json_data).length !== 0);

  return json_array.flat(1).map((item) => item.link);
}

async function find_class(site, html_class) {
  const stream = fs.createWriteStream('data.txt')
  let endpoint = to_post_endpoint(site.url);
  let pages = get_posts(endpoint[1]);
  let posts = get_posts(endpoint[0]);

  var [all_pages, all_posts] = await Promise.all([pages, posts]);

  var all = all_pages.concat(all_posts);

  for (let item of all) {
    var data = await jQuery.get(item).catch((error) => console.log(error));
    var nodes = jQuery.parseHTML(data);
    var classes = jQuery(nodes).find(`${html_class}`);
    var result = [item, classes.length];
    if (result[1] > 0) {
      stream.write(result + '\n');
    }
  }
  stream.end();
}

var selector = "section.nau-block-panels";

get_all_NAU_sites().then((sites) => {
  for (let site of sites) {
    find_class(site, selector)
  }
}).catch((error) => console.log(error))