def assert_blog_id_schema(blog_id: str) -> None:
    if not blog_id.replace('-', '').replace('_', '').isalnum():
        raise ValueError("blog_id seems to be incorrect. Are there spaces?")


def assert_post_id_schema(post_id: str) -> None:
    if not post_id.isdecimal():
        raise ValueError("post_id should contain digits (0-9) only.")
