# Git Configuration

When you're collaborating on projects with Git and GitHub, Git might produce unexpected results if, for example, you're working on a Windows machine, and your collaborator has made a change in macOS.

You can configure Git to handle line endings automatically so you can collaborate effectively with people who use different operating systems.

The `git config core.autocrlf` command is used to change how Git handles line endings. It takes a single argument.

## On Mac

```bash
$ git config --global core.autocrlf input
# Configure Git to ensure line endings in files you checkout are correct for macOS
```

## On Windows

```bash
$ git config --global core.autocrlf true
# Configure Git to ensure line endings in files you checkout are correct for Windows.
# For compatibility, line endings are converted to Unix style when you commit files.
```

## On Linux

```bash
$ git config --global core.autocrlf input
# Configure Git to ensure line endings in files you checkout are correct for Linux
```

## Per-repository settings

Optionally, you can configure a _.gitattributes_ file to manage how Git reads line endings in a specific repository. When you commit this file to a repository, it overrides the `core.autocrlf` setting for all repository contributors. This ensures consistent behavior for all users, regardless of their Git settings and environment.

The .gitattributes file must be created in the root of the repository and committed like any other file.

A .gitattributes file looks like a table with two columns:

On the left is the file name for Git to match.
On the right is the line ending configuration that Git should use for those files.

### Example

Here's an example _.gitattributes_ file. You can use it as a template for your repositories:

```bash
# Set the default behavior, in case people don't have core.autocrlf set.
* text=auto

# Explicitly declare text files you want to always be normalized and converted
# to native line endings on checkout.
*.py text

# Declare files that will always have CRLF line endings on checkout.
*.sln text eol=crlf

# Denote all files that are truly binary and should not be modified.
*.png binary
*.jpg binary
```

From [Configuring Git to handle line endings](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings).
