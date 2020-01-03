import os
import datetime
import logging
import logging.config
import gitlab
from fs import open_fs
from fs.copy import copy_file

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))

LOGGER = logging.getLogger()

GITLAB_URL = 'https://gitlab.com/'


def main():
    """
    This script iterates over a group of gitlab projects and generates a script that either clones
    the projects if they don't exist or pulls the project, if it does. The project group structure
    is preserved.
    """
    gl = gitlab.Gitlab(
        os.environ.get('GITLAB_URL', GITLAB_URL), private_token=os.environ['GITLAB_PRIVATE_TOKEN']
    )

    script_name = os.environ.get('SCRIPT_NAME', 'gitlab-download.sh')

    with open_fs('mem://') as output_path:
        output_path.writetext(script_name, f'# generated: {datetime.datetime.now()}\n')
        output_path.appendtext(
            script_name,
            'clone_or_pull() {\n'
            'if [ -e "$1" ]; then\necho $1\ngit -C $1 pull\nelse\ngit clone $2 $1\nfi\n}\n'
        )
        for group in gl.groups.list(all_available=True, all=True):
            if group.full_path.startswith(os.environ['GITLAB_GROUP_PATH']):
                LOGGER.info(group.name)
                for project in group.projects.list(all=True):
                    if project.repository_access_level != 'disabled':
                        output_path.appendtext(script_name, (
                            f'clone_or_pull '
                            f'{project.path_with_namespace} {project.ssh_url_to_repo}\n'
                        ))

        copy_file(output_path, script_name, os.environ['OUTPUT_PATH'], script_name)


if __name__ == "__main__":
    main()
