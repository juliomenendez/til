from pathlib import Path
from datetime import timezone
import re
import git
import sys

root = Path(__file__).parent.resolve()

index_re = re.compile(r"<!\-\- index starts \-\->.*<!\-\- index ends \-\->", re.DOTALL)
count_re = re.compile(r"<!\-\- count starts \-\->.*<!\-\- count ends \-\->", re.DOTALL)

COUNT_TEMPLATE = "<!-- count starts -->{}<!-- count ends -->"

def created_changed_times(repo_path, ref="main"):
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref)))
    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times

def build_topic_entries_dict(repo_path):
    all_times = created_changed_times(repo_path)
    by_topic = {}
    for filepath in repo_path.glob("*/*.md"):
        fp = filepath.open()
        title = fp.readline().lstrip("#").strip()
        path = str(filepath.relative_to(repo_path)).replace('\\', '/')
        slug = filepath.stem
        url = "https://github.com/juliomenendez/til/blob/main/{}".format(path)
        # Do we need to render the markdown?
        path_slug = path.replace("/", "_")
        topic = path.split("/")[0]
        record = {
            "path": path_slug,
            "slug": slug,
            "topic": topic,
            "title": title,
            "url": url,
            **all_times[path],
        }
        by_topic.setdefault(topic, []).append(record)
    
    return by_topic

if __name__ == "__main__":
    by_topic = build_topic_entries_dict(root)
    index = ["<!-- index starts -->"]
    count = 0
    for topic, rows in by_topic.items():
        count += len(rows)
        index.append("## {}\n".format(topic))
        for row in rows:
            index.append(
                "* [{title}]({url}) - {date}".format(
                    date=row["created"].split("T")[0], **row
                )
            )
        index.append("")
    if index[-1] == "":
        index.pop()
    index.append("<!-- index ends -->")
    if "--rewrite" in sys.argv:
        readme = root / "README.md"
        index_txt = "\n".join(index).strip()
        readme_contents = readme.open().read()
        rewritten = index_re.sub(index_txt, readme_contents)
        rewritten = count_re.sub(COUNT_TEMPLATE.format(count), rewritten)
        readme.open("w").write(rewritten)
    else:
        print("\n".join(index))