# Yizhong Sun Academic Homepage

This is the source for Yizhong Sun's academic homepage, based on AcadHomepage/Jekyll and designed for GitHub Pages.

## Local Preview

Install Ruby and Bundler, then run:

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000`.

On Ruby 3.2 with the GitHub Pages 215 dependency set, Liquid 4.0.3 may need a
local compatibility shim because Ruby removed `Object#tainted?`. For a local
build on this machine, run:

```powershell
& 'C:\Ruby32-x64\bin\bundle.bat' exec 'C:\Ruby32-x64\bin\ruby.exe' -e "class Object; def tainted?; false; end; end; load 'C:/Ruby32-x64/bin/jekyll'" build
```

## Main Files

- `_config.yml` controls site metadata and sidebar profile links.
- `_pages/about.md` contains the homepage content.
- `images/profile.jpg` is the sidebar profile image.
- `images/profile-hero-office.jpg` is used in the homepage opening section.
- `My_CV__1_.pdf` is the downloadable CV.
