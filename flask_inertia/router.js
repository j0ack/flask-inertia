/**
 * MIT License
 *
 * Copyright (c) 2019-2021 Morgan Aubert
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * code from https://github.com/ellmetha/django-js-routes/
**/

window.routes = {{ routes | tojson }};

window.reverseUrl = function(urlName) {
  let url = window.routes[urlName];
  if (!url) {
    throw "URL " + urlName + " was not found.";
  }

  const args = arguments;
  const argTokens = url.match(/\u003c\w*\u003e/g);
  if (!argTokens && args[1] !== undefined) {
    throw "Invalid URL lookup: URL " + urlName + " does not expect any arguments.";
  }

  if (typeof (args[1]) == 'object' && !Array.isArray(args[1])) {
    argTokens.forEach(function(token) {
      const argName = token.slice(1, -1);
      const argValue = args[1][argName];
      if (argValue === undefined) {
        throw "Invalid URL lookup: Argument " + argName + " was not provided.";
      }
      url = url.replace(token, argValue);
    });
  } else if (args[1] !== undefined) {
    const argsArray = Array.isArray(args[1]) ? args[1] : Array.prototype.slice.apply(args, [1, args.length]);
    if (argTokens.length !== argsArray.length) {
      throw "Invalid URL lookup: Wrong number of arguments ; expected " + argTokens.length.toString() " arguments.`;
    }

    argTokens.forEach(function(token, i) {
      const argValue = argsArray[i];
      url = url.replace(token, argValue);
    });
  }

  return url;
};
