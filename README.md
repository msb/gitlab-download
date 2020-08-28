npm install package-info
(async () => {
    console.log(await info('@ucam.uis.devops/choose-columns-dialog'));
})();

This is a containerised script that iterates over a tree of gitlab projects and generates a bash 
script that either clones the projects if they don't exist or pulls the project, if it does. The
tree structure is preserved.

To run the script in it's simplest form, create a `gitlabdownload.env` file with the following
variables:

```
GITLAB_URL=[the host name for gitlab]
GITLAB_PRIVATE_TOKEN=[a gitlab personal access token]
GITLAB_GROUP_PATH=[the path of the group to download]
```

Then running the following docker command will output the script to the current working directory:

```bash
export VERSION=1.0

docker run --rm \
  --env-file gitlabdownload.env \
  --user $(id -u):$(id -g) --volume "$PWD:/data" \
  msb140610/gitlab-download:$VERSION
```

The script uses [PyFilesystem](https://github.com/pyfilesystem/pyfilesystem2) to write to the
output path so the script can be configured to write to any file system supported by PyFilesystem
which could be useful if you aren't running docker locally. The container has been configured with
the `fs.dropboxfs`, `fs.onedrivefs`, & `fs.googledrivefs`.

### Configuring the output path with fs.googledrivefs

There are different ways of authenticating to GDrive API but this example uses a service account
with permission on the target directory. The set up steps are sketched as follows:

 - create a GCP project
 - In that project:
   - create a GCP service account, downloading it's credentials file
   - enable the GDrive API
 - Allow the service account read/write permission on the target GDrive folder 
   (use it's email address)
 - Note the id of the target GDrive folder 

Then update the `gitlabdownload.env` file with the following variables:

```
GOOGLE_APPLICATION_CREDENTIALS=/credentials.json
OUTPUT_PATH=googledrive:///?root_id={the id of the target GDrive folder}
# the default for OUTPUT_PATH is: osfs:///data
```

Finally, run the container and the generated script with be written to the target GDrive folder
with no need for a bind volume.

```bash
docker run --rm --env-file gitlabdownload.env \
  --volume [path/to/credentials]:/credentials.json \
  msb140610/gitlab-download:$VERSION
```

This is quite a lot of effort for a trivial script but it was a learning exercise and quite
helpful in understanding PyFilesystem and the GDrive API. 

### Development

If you wish to make changes to the script then the source for the script and container
configuration can be cloned from [github](https://github.com/msb/gitlab-download). Once cloned the
script can be from the local project using a bind volume as follows:

```bash
docker run --rm \
  --env-file gitlabdownload.env \
  --volume "$PWD:/app" \
  msb140610/gitlab-download:$VERSION
```
Also the container has been configured with `ipython` if you wish to experiment with the gitlab
or PyFilesystem libraries as follows:

```bash
docker run --rm -it \
  --env-file gitlabdownload.env \
  --volume "$PWD:/app" \
  --entrypoint ipython \
  msb140610/gitlab-download:$VERSION
```

If the container configuration needs changing, it can be built for testing locally as follows:

```bash
docker build -t gitlab-download .
```
