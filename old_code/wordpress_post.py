from datetime import datetime, timedelta
import glob
if glob.glob("config.py"):
    import config
else:
    import github_config as config
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import WordPressPost

client = Client(config.my_site, config.user, config.password)
# print(posting.split(","))


def posting_test(heading, df):
    posting = client.call(posts.GetPosts())
    posting = [str(i) for i in posting]
    for j, p in enumerate(posting):
        [p.replace(i, '') for i in config.special]
        posting[j] = p
    print(posting, heading)
    # name = config.novel_link + heading.lower().replace(" ", "-") + "/"
    if heading == "Works related" or heading == "Let's see what we are doing":
        return "Summary post seprately"
    elif heading in posting or heading in df['name'].to_list():
        return "Already posted"
    else:
        return "Need to be posted"


def posting(heading, content):
    print(heading)
    # heading = 'test'
    post = WordPressPost()
    post.title = heading
    post.terms_names = {
        'post_tag': config.tags,
        'category': [config.novel_name],
    }
    post.content = content
    post.id = client.call(posts.NewPost(post))
    post.date = datetime.now() + timedelta(days=7)
    post.post_status = 'publish'
    client.call(posts.EditPost(post.id, post))
    print(post)
    return post.id


def uploadImage(novel_img, img_data):
    data = {
        'name': novel_img,
        'type': 'image/jpeg',
    }
    data['bits'] = xmlrpc_client.Binary(img_data)
    response = client.call(media.UploadFile(data))
    attachment_id = response['id']
    return attachment_id
