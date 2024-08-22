## Contents

- [Getting started](#getting-started-)
- [Usage](#usage)
- [FAQ](#faq-)
- [License](#license-)

---

## Getting started 🐣

This is a generated search experience created with [Search UI](https://github.com/elastic/search-ui).

To set up and run this project, follow the instructions below.

Requires [npm](https://www.npmjs.com/).

Dependencies:
- Node v16.13.0

One can leverage [NVM](https://github.com/nvm-sh/nvm) to install Node before proceeding to start the application by running the following commands:

```bash
# Run this to install Node 16.13.0
nvm install 16.13.0

# Run this to use the installed Node version 
nvm use 16.13.0
```

Run the following commands to start this application:

```bash
# Run the `cd` command to change the current directory to the
# location of your downloaded Reference UI. Replace the path
# below with the actual path of your project.
cd ~/Downloads/app-search-reference-ui

# Run this to set everything up
npm install

# Run this to start your application and open it up in a new browser window
npm start
```

## Usage

### Updating configuration

The project is configured via a JSON [config file](src/config/engine.json). This file has been automatically generated for you when downloading this project. If you would like to make configuration changes, there is no need to regenerate this app from your App Search Dashboard. Additional configuration can be made by modifying that file.

You can simply open up the
[engine.json](src/config/engine.json) file, update the [options](#config),
and then restart this app.

### Configuration options <a id="config"></a>

The following is a complete list of options available for configuration in [engine.json](src/config/engine.json).

| option               | value type    | required/optional | source                                                                                                                                                                                          |
| -------------------- | ------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `engineName`         | String        | required          | Found in your App Search Dashboard.                                                                                                                                                             |
| `endpointBase`       | String        | required*         | (*) Elastic Enterprise Search deployment URL, example: "http://127.0.0.1:3002".                                                                                                                 |
| `searchKey`          | String        | required          | Found in your App Search Dashboard.                                                                                                                                                             |
| `searchFields`       | Array[String] | required          | A list of fields that will be searched with your search term.                                                                                                                                   |
| `resultFields`       | Array[String] | required          | A list of fields that will be displayed within your results.                                                                                                                                    |
| `querySuggestFields` | Array[String] | optional          | A list of fields that will be searched and displayed as query suggestions.                                                                                                                      |
| `titleField`         | String        | optional          | The field to display as the title in results.                                                                                                                                                   |
| `urlField`           | String        | optional          | A field with a url to use as a link in results.                                                                                                                                                 |
| `sortFields`         | Array[String] | optional          | A list of fields that will be used for sort options.                                                                                                                                            |
| `facets`             | Array[String] | optional          | A list of fields that will be available as "facet" filters. Read more about facets within the [App Search documentation](https://www.elastic.co/guide/en/app-search/current/facets-guide.html). |

## Building and embedding

To embed this application into a website, it can be built into static assets using the following command:
```
npm run build
```

This will create two files in the `build` directory:
```
build/static/js/main.<hash>.js
build/static/css/main.<hash>.css
```

Include the built static assets as well as an element with `id="root"`. For example:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <script defer="defer" src="/static/js/main.<hash>.js"></script>
    <link href="/static/css/main.<hash>.css" rel="stylesheet" />
  </head>
  <body>
    <div id="root" class="app-container"></div>
  </body>
</html>
```

## Deploy and Share

This app can be easily published to any server as static assets and served. We recommend [Netlify](https://www.netlify.com/), but you have other [options](https://facebook.github.io/create-react-app/docs/deployment) as well.

To deploy:

```
npm run build
npm install netlify-cli -g
netlify deploy # enter ./build as the deploy path
```

You'll then simply follow the command prompt to log into Netlify and deploy your site. This can be completed in just a few minutes.

### External configuration

If you are embedding this app inside of another page, and you would like to
source the configuration from outside of the `engine.json` file,
you can simply write the configuration directly to `window.appConfig`.

### If you are checking this project out directly from GitHub... <a id="github"></a>

You can follow the previous steps, but then you will need to create and configure
[engine.json](src/config/engine.json).

To do so, make a copy of [engine.json.example](src/config/engine.json.example),
rename it to `engine.json` and configure it with your Engine's specific details.

```bash
cp src/config/engine.json.example src/config/engine.json
```

## Customization

This project is built with [Search UI](https://github.com/elastic/search-ui), which is a React library for building search experiences. If you're interested in using this project as a base for your own, most of
what you'll need can be found in the Search UI documentation.

## FAQ 🔮

### Where do I report issues with this application?

If something is not working as expected, please open an [issue](https://github.com/elastic/app-search-reference-ui-react/issues/new).


### Where else can I go to get help?

You can checkout the [Elastic Enterprise Search community discuss forums](https://discuss.elastic.co/c/enterprise-search/84).

## License 📗

[Apache-2.0](https://github.com/elastic/app-search-reference-ui-react/blob/master/LICENSE.txt) © [Elastic](https://github.com/elastic)
