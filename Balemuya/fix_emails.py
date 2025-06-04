def commit_callback(commit):
    if commit.author_email == b"":
        commit.author_email = b"yikeber50@gmail.com"
        commit.author_name = b"Yikeber"
    if commit.committer_email == b"":
        commit.committer_email = b"yikeber50@gmail.com"
        commit.committer_name = b"Yikeber"
