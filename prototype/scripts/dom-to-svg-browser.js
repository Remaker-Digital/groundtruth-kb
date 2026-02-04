(() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    // If the importer is in node compatibility mode or this is not an ESM
    // file that has been converted to a CommonJS file using a Babel-
    // compatible transform (i.e. "__esModule" has not been set), then set
    // "default" to the CommonJS "module.exports" for node compatibility.
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));

  // node_modules/picocolors/picocolors.browser.js
  var require_picocolors_browser = __commonJS({
    "node_modules/picocolors/picocolors.browser.js"(exports, module) {
      var x = String;
      var create = function() {
        return { isColorSupported: false, reset: x, bold: x, dim: x, italic: x, underline: x, inverse: x, hidden: x, strikethrough: x, black: x, red: x, green: x, yellow: x, blue: x, magenta: x, cyan: x, white: x, gray: x, bgBlack: x, bgRed: x, bgGreen: x, bgYellow: x, bgBlue: x, bgMagenta: x, bgCyan: x, bgWhite: x, blackBright: x, redBright: x, greenBright: x, yellowBright: x, blueBright: x, magentaBright: x, cyanBright: x, whiteBright: x, bgBlackBright: x, bgRedBright: x, bgGreenBright: x, bgYellowBright: x, bgBlueBright: x, bgMagentaBright: x, bgCyanBright: x, bgWhiteBright: x };
      };
      module.exports = create();
      module.exports.createColors = create;
    }
  });

  // (disabled):node_modules/postcss/lib/terminal-highlight
  var require_terminal_highlight = __commonJS({
    "(disabled):node_modules/postcss/lib/terminal-highlight"() {
    }
  });

  // node_modules/postcss/lib/css-syntax-error.js
  var require_css_syntax_error = __commonJS({
    "node_modules/postcss/lib/css-syntax-error.js"(exports, module) {
      "use strict";
      var pico = require_picocolors_browser();
      var terminalHighlight = require_terminal_highlight();
      var CssSyntaxError2 = class _CssSyntaxError extends Error {
        constructor(message, line, column, source, file, plugin2) {
          super(message);
          this.name = "CssSyntaxError";
          this.reason = message;
          if (file) {
            this.file = file;
          }
          if (source) {
            this.source = source;
          }
          if (plugin2) {
            this.plugin = plugin2;
          }
          if (typeof line !== "undefined" && typeof column !== "undefined") {
            if (typeof line === "number") {
              this.line = line;
              this.column = column;
            } else {
              this.line = line.line;
              this.column = line.column;
              this.endLine = column.line;
              this.endColumn = column.column;
            }
          }
          this.setMessage();
          if (Error.captureStackTrace) {
            Error.captureStackTrace(this, _CssSyntaxError);
          }
        }
        setMessage() {
          this.message = this.plugin ? this.plugin + ": " : "";
          this.message += this.file ? this.file : "<css input>";
          if (typeof this.line !== "undefined") {
            this.message += ":" + this.line + ":" + this.column;
          }
          this.message += ": " + this.reason;
        }
        showSourceCode(color) {
          if (!this.source) return "";
          let css = this.source;
          if (color == null) color = pico.isColorSupported;
          let aside = (text) => text;
          let mark = (text) => text;
          let highlight = (text) => text;
          if (color) {
            let { bold, gray, red } = pico.createColors(true);
            mark = (text) => bold(red(text));
            aside = (text) => gray(text);
            if (terminalHighlight) {
              highlight = (text) => terminalHighlight(text);
            }
          }
          let lines = css.split(/\r?\n/);
          let start = Math.max(this.line - 3, 0);
          let end = Math.min(this.line + 2, lines.length);
          let maxWidth = String(end).length;
          return lines.slice(start, end).map((line, index) => {
            let number = start + 1 + index;
            let gutter = " " + (" " + number).slice(-maxWidth) + " | ";
            if (number === this.line) {
              if (line.length > 160) {
                let padding = 20;
                let subLineStart = Math.max(0, this.column - padding);
                let subLineEnd = Math.max(
                  this.column + padding,
                  this.endColumn + padding
                );
                let subLine = line.slice(subLineStart, subLineEnd);
                let spacing2 = aside(gutter.replace(/\d/g, " ")) + line.slice(0, Math.min(this.column - 1, padding - 1)).replace(/[^\t]/g, " ");
                return mark(">") + aside(gutter) + highlight(subLine) + "\n " + spacing2 + mark("^");
              }
              let spacing = aside(gutter.replace(/\d/g, " ")) + line.slice(0, this.column - 1).replace(/[^\t]/g, " ");
              return mark(">") + aside(gutter) + highlight(line) + "\n " + spacing + mark("^");
            }
            return " " + aside(gutter) + highlight(line);
          }).join("\n");
        }
        toString() {
          let code = this.showSourceCode();
          if (code) {
            code = "\n\n" + code + "\n";
          }
          return this.name + ": " + this.message + code;
        }
      };
      module.exports = CssSyntaxError2;
      CssSyntaxError2.default = CssSyntaxError2;
    }
  });

  // node_modules/postcss/lib/stringifier.js
  var require_stringifier = __commonJS({
    "node_modules/postcss/lib/stringifier.js"(exports, module) {
      "use strict";
      var DEFAULT_RAW = {
        after: "\n",
        beforeClose: "\n",
        beforeComment: "\n",
        beforeDecl: "\n",
        beforeOpen: " ",
        beforeRule: "\n",
        colon: ": ",
        commentLeft: " ",
        commentRight: " ",
        emptyBody: "",
        indent: "    ",
        semicolon: false
      };
      function capitalize(str) {
        return str[0].toUpperCase() + str.slice(1);
      }
      var Stringifier = class {
        constructor(builder) {
          this.builder = builder;
        }
        atrule(node, semicolon) {
          let name = "@" + node.name;
          let params = node.params ? this.rawValue(node, "params") : "";
          if (typeof node.raws.afterName !== "undefined") {
            name += node.raws.afterName;
          } else if (params) {
            name += " ";
          }
          if (node.nodes) {
            this.block(node, name + params);
          } else {
            let end = (node.raws.between || "") + (semicolon ? ";" : "");
            this.builder(name + params + end, node);
          }
        }
        beforeAfter(node, detect) {
          let value;
          if (node.type === "decl") {
            value = this.raw(node, null, "beforeDecl");
          } else if (node.type === "comment") {
            value = this.raw(node, null, "beforeComment");
          } else if (detect === "before") {
            value = this.raw(node, null, "beforeRule");
          } else {
            value = this.raw(node, null, "beforeClose");
          }
          let buf = node.parent;
          let depth = 0;
          while (buf && buf.type !== "root") {
            depth += 1;
            buf = buf.parent;
          }
          if (value.includes("\n")) {
            let indent = this.raw(node, null, "indent");
            if (indent.length) {
              for (let step = 0; step < depth; step++) value += indent;
            }
          }
          return value;
        }
        block(node, start) {
          let between = this.raw(node, "between", "beforeOpen");
          this.builder(start + between + "{", node, "start");
          let after;
          if (node.nodes && node.nodes.length) {
            this.body(node);
            after = this.raw(node, "after");
          } else {
            after = this.raw(node, "after", "emptyBody");
          }
          if (after) this.builder(after);
          this.builder("}", node, "end");
        }
        body(node) {
          let last = node.nodes.length - 1;
          while (last > 0) {
            if (node.nodes[last].type !== "comment") break;
            last -= 1;
          }
          let semicolon = this.raw(node, "semicolon");
          for (let i = 0; i < node.nodes.length; i++) {
            let child = node.nodes[i];
            let before = this.raw(child, "before");
            if (before) this.builder(before);
            this.stringify(child, last !== i || semicolon);
          }
        }
        comment(node) {
          let left = this.raw(node, "left", "commentLeft");
          let right = this.raw(node, "right", "commentRight");
          this.builder("/*" + left + node.text + right + "*/", node);
        }
        decl(node, semicolon) {
          let between = this.raw(node, "between", "colon");
          let string = node.prop + between + this.rawValue(node, "value");
          if (node.important) {
            string += node.raws.important || " !important";
          }
          if (semicolon) string += ";";
          this.builder(string, node);
        }
        document(node) {
          this.body(node);
        }
        raw(node, own, detect) {
          let value;
          if (!detect) detect = own;
          if (own) {
            value = node.raws[own];
            if (typeof value !== "undefined") return value;
          }
          let parent = node.parent;
          if (detect === "before") {
            if (!parent || parent.type === "root" && parent.first === node) {
              return "";
            }
            if (parent && parent.type === "document") {
              return "";
            }
          }
          if (!parent) return DEFAULT_RAW[detect];
          let root2 = node.root();
          if (!root2.rawCache) root2.rawCache = {};
          if (typeof root2.rawCache[detect] !== "undefined") {
            return root2.rawCache[detect];
          }
          if (detect === "before" || detect === "after") {
            return this.beforeAfter(node, detect);
          } else {
            let method = "raw" + capitalize(detect);
            if (this[method]) {
              value = this[method](root2, node);
            } else {
              root2.walk((i) => {
                value = i.raws[own];
                if (typeof value !== "undefined") return false;
              });
            }
          }
          if (typeof value === "undefined") value = DEFAULT_RAW[detect];
          root2.rawCache[detect] = value;
          return value;
        }
        rawBeforeClose(root2) {
          let value;
          root2.walk((i) => {
            if (i.nodes && i.nodes.length > 0) {
              if (typeof i.raws.after !== "undefined") {
                value = i.raws.after;
                if (value.includes("\n")) {
                  value = value.replace(/[^\n]+$/, "");
                }
                return false;
              }
            }
          });
          if (value) value = value.replace(/\S/g, "");
          return value;
        }
        rawBeforeComment(root2, node) {
          let value;
          root2.walkComments((i) => {
            if (typeof i.raws.before !== "undefined") {
              value = i.raws.before;
              if (value.includes("\n")) {
                value = value.replace(/[^\n]+$/, "");
              }
              return false;
            }
          });
          if (typeof value === "undefined") {
            value = this.raw(node, null, "beforeDecl");
          } else if (value) {
            value = value.replace(/\S/g, "");
          }
          return value;
        }
        rawBeforeDecl(root2, node) {
          let value;
          root2.walkDecls((i) => {
            if (typeof i.raws.before !== "undefined") {
              value = i.raws.before;
              if (value.includes("\n")) {
                value = value.replace(/[^\n]+$/, "");
              }
              return false;
            }
          });
          if (typeof value === "undefined") {
            value = this.raw(node, null, "beforeRule");
          } else if (value) {
            value = value.replace(/\S/g, "");
          }
          return value;
        }
        rawBeforeOpen(root2) {
          let value;
          root2.walk((i) => {
            if (i.type !== "decl") {
              value = i.raws.between;
              if (typeof value !== "undefined") return false;
            }
          });
          return value;
        }
        rawBeforeRule(root2) {
          let value;
          root2.walk((i) => {
            if (i.nodes && (i.parent !== root2 || root2.first !== i)) {
              if (typeof i.raws.before !== "undefined") {
                value = i.raws.before;
                if (value.includes("\n")) {
                  value = value.replace(/[^\n]+$/, "");
                }
                return false;
              }
            }
          });
          if (value) value = value.replace(/\S/g, "");
          return value;
        }
        rawColon(root2) {
          let value;
          root2.walkDecls((i) => {
            if (typeof i.raws.between !== "undefined") {
              value = i.raws.between.replace(/[^\s:]/g, "");
              return false;
            }
          });
          return value;
        }
        rawEmptyBody(root2) {
          let value;
          root2.walk((i) => {
            if (i.nodes && i.nodes.length === 0) {
              value = i.raws.after;
              if (typeof value !== "undefined") return false;
            }
          });
          return value;
        }
        rawIndent(root2) {
          if (root2.raws.indent) return root2.raws.indent;
          let value;
          root2.walk((i) => {
            let p = i.parent;
            if (p && p !== root2 && p.parent && p.parent === root2) {
              if (typeof i.raws.before !== "undefined") {
                let parts = i.raws.before.split("\n");
                value = parts[parts.length - 1];
                value = value.replace(/\S/g, "");
                return false;
              }
            }
          });
          return value;
        }
        rawSemicolon(root2) {
          let value;
          root2.walk((i) => {
            if (i.nodes && i.nodes.length && i.last.type === "decl") {
              value = i.raws.semicolon;
              if (typeof value !== "undefined") return false;
            }
          });
          return value;
        }
        rawValue(node, prop) {
          let value = node[prop];
          let raw = node.raws[prop];
          if (raw && raw.value === value) {
            return raw.raw;
          }
          return value;
        }
        root(node) {
          this.body(node);
          if (node.raws.after) this.builder(node.raws.after);
        }
        rule(node) {
          this.block(node, this.rawValue(node, "selector"));
          if (node.raws.ownSemicolon) {
            this.builder(node.raws.ownSemicolon, node, "end");
          }
        }
        stringify(node, semicolon) {
          if (!this[node.type]) {
            throw new Error(
              "Unknown AST node type " + node.type + ". Maybe you need to change PostCSS stringifier."
            );
          }
          this[node.type](node, semicolon);
        }
      };
      module.exports = Stringifier;
      Stringifier.default = Stringifier;
    }
  });

  // node_modules/postcss/lib/stringify.js
  var require_stringify = __commonJS({
    "node_modules/postcss/lib/stringify.js"(exports, module) {
      "use strict";
      var Stringifier = require_stringifier();
      function stringify2(node, builder) {
        let str = new Stringifier(builder);
        str.stringify(node);
      }
      module.exports = stringify2;
      stringify2.default = stringify2;
    }
  });

  // node_modules/postcss/lib/symbols.js
  var require_symbols = __commonJS({
    "node_modules/postcss/lib/symbols.js"(exports, module) {
      "use strict";
      module.exports.isClean = Symbol("isClean");
      module.exports.my = Symbol("my");
    }
  });

  // node_modules/postcss/lib/node.js
  var require_node = __commonJS({
    "node_modules/postcss/lib/node.js"(exports, module) {
      "use strict";
      var CssSyntaxError2 = require_css_syntax_error();
      var Stringifier = require_stringifier();
      var stringify2 = require_stringify();
      var { isClean, my } = require_symbols();
      function cloneNode(obj, parent) {
        let cloned = new obj.constructor();
        for (let i in obj) {
          if (!Object.prototype.hasOwnProperty.call(obj, i)) {
            continue;
          }
          if (i === "proxyCache") continue;
          let value = obj[i];
          let type = typeof value;
          if (i === "parent" && type === "object") {
            if (parent) cloned[i] = parent;
          } else if (i === "source") {
            cloned[i] = value;
          } else if (Array.isArray(value)) {
            cloned[i] = value.map((j) => cloneNode(j, cloned));
          } else {
            if (type === "object" && value !== null) value = cloneNode(value);
            cloned[i] = value;
          }
        }
        return cloned;
      }
      function sourceOffset(inputCSS, position) {
        if (position && typeof position.offset !== "undefined") {
          return position.offset;
        }
        let column = 1;
        let line = 1;
        let offset = 0;
        for (let i = 0; i < inputCSS.length; i++) {
          if (line === position.line && column === position.column) {
            offset = i;
            break;
          }
          if (inputCSS[i] === "\n") {
            column = 1;
            line += 1;
          } else {
            column += 1;
          }
        }
        return offset;
      }
      var Node3 = class {
        get proxyOf() {
          return this;
        }
        constructor(defaults2 = {}) {
          this.raws = {};
          this[isClean] = false;
          this[my] = true;
          for (let name in defaults2) {
            if (name === "nodes") {
              this.nodes = [];
              for (let node of defaults2[name]) {
                if (typeof node.clone === "function") {
                  this.append(node.clone());
                } else {
                  this.append(node);
                }
              }
            } else {
              this[name] = defaults2[name];
            }
          }
        }
        addToError(error) {
          error.postcssNode = this;
          if (error.stack && this.source && /\n\s{4}at /.test(error.stack)) {
            let s = this.source;
            error.stack = error.stack.replace(
              /\n\s{4}at /,
              `$&${s.input.from}:${s.start.line}:${s.start.column}$&`
            );
          }
          return error;
        }
        after(add) {
          this.parent.insertAfter(this, add);
          return this;
        }
        assign(overrides = {}) {
          for (let name in overrides) {
            this[name] = overrides[name];
          }
          return this;
        }
        before(add) {
          this.parent.insertBefore(this, add);
          return this;
        }
        cleanRaws(keepBetween) {
          delete this.raws.before;
          delete this.raws.after;
          if (!keepBetween) delete this.raws.between;
        }
        clone(overrides = {}) {
          let cloned = cloneNode(this);
          for (let name in overrides) {
            cloned[name] = overrides[name];
          }
          return cloned;
        }
        cloneAfter(overrides = {}) {
          let cloned = this.clone(overrides);
          this.parent.insertAfter(this, cloned);
          return cloned;
        }
        cloneBefore(overrides = {}) {
          let cloned = this.clone(overrides);
          this.parent.insertBefore(this, cloned);
          return cloned;
        }
        error(message, opts = {}) {
          if (this.source) {
            let { end, start } = this.rangeBy(opts);
            return this.source.input.error(
              message,
              { column: start.column, line: start.line },
              { column: end.column, line: end.line },
              opts
            );
          }
          return new CssSyntaxError2(message);
        }
        getProxyProcessor() {
          return {
            get(node, prop) {
              if (prop === "proxyOf") {
                return node;
              } else if (prop === "root") {
                return () => node.root().toProxy();
              } else {
                return node[prop];
              }
            },
            set(node, prop, value) {
              if (node[prop] === value) return true;
              node[prop] = value;
              if (prop === "prop" || prop === "value" || prop === "name" || prop === "params" || prop === "important" || /* c8 ignore next */
              prop === "text") {
                node.markDirty();
              }
              return true;
            }
          };
        }
        /* c8 ignore next 3 */
        markClean() {
          this[isClean] = true;
        }
        markDirty() {
          if (this[isClean]) {
            this[isClean] = false;
            let next = this;
            while (next = next.parent) {
              next[isClean] = false;
            }
          }
        }
        next() {
          if (!this.parent) return void 0;
          let index = this.parent.index(this);
          return this.parent.nodes[index + 1];
        }
        positionBy(opts = {}) {
          let pos = this.source.start;
          if (opts.index) {
            pos = this.positionInside(opts.index);
          } else if (opts.word) {
            let inputString = "document" in this.source.input ? this.source.input.document : this.source.input.css;
            let stringRepresentation = inputString.slice(
              sourceOffset(inputString, this.source.start),
              sourceOffset(inputString, this.source.end)
            );
            let index = stringRepresentation.indexOf(opts.word);
            if (index !== -1) pos = this.positionInside(index);
          }
          return pos;
        }
        positionInside(index) {
          let column = this.source.start.column;
          let line = this.source.start.line;
          let inputString = "document" in this.source.input ? this.source.input.document : this.source.input.css;
          let offset = sourceOffset(inputString, this.source.start);
          let end = offset + index;
          for (let i = offset; i < end; i++) {
            if (inputString[i] === "\n") {
              column = 1;
              line += 1;
            } else {
              column += 1;
            }
          }
          return { column, line, offset: end };
        }
        prev() {
          if (!this.parent) return void 0;
          let index = this.parent.index(this);
          return this.parent.nodes[index - 1];
        }
        rangeBy(opts = {}) {
          let inputString = "document" in this.source.input ? this.source.input.document : this.source.input.css;
          let start = {
            column: this.source.start.column,
            line: this.source.start.line,
            offset: sourceOffset(inputString, this.source.start)
          };
          let end = this.source.end ? {
            column: this.source.end.column + 1,
            line: this.source.end.line,
            offset: typeof this.source.end.offset === "number" ? (
              // `source.end.offset` is exclusive, so we don't need to add 1
              this.source.end.offset
            ) : (
              // Since line/column in this.source.end is inclusive,
              // the `sourceOffset(... , this.source.end)` returns an inclusive offset.
              // So, we add 1 to convert it to exclusive.
              sourceOffset(inputString, this.source.end) + 1
            )
          } : {
            column: start.column + 1,
            line: start.line,
            offset: start.offset + 1
          };
          if (opts.word) {
            let stringRepresentation = inputString.slice(
              sourceOffset(inputString, this.source.start),
              sourceOffset(inputString, this.source.end)
            );
            let index = stringRepresentation.indexOf(opts.word);
            if (index !== -1) {
              start = this.positionInside(index);
              end = this.positionInside(index + opts.word.length);
            }
          } else {
            if (opts.start) {
              start = {
                column: opts.start.column,
                line: opts.start.line,
                offset: sourceOffset(inputString, opts.start)
              };
            } else if (opts.index) {
              start = this.positionInside(opts.index);
            }
            if (opts.end) {
              end = {
                column: opts.end.column,
                line: opts.end.line,
                offset: sourceOffset(inputString, opts.end)
              };
            } else if (typeof opts.endIndex === "number") {
              end = this.positionInside(opts.endIndex);
            } else if (opts.index) {
              end = this.positionInside(opts.index + 1);
            }
          }
          if (end.line < start.line || end.line === start.line && end.column <= start.column) {
            end = {
              column: start.column + 1,
              line: start.line,
              offset: start.offset + 1
            };
          }
          return { end, start };
        }
        raw(prop, defaultType) {
          let str = new Stringifier();
          return str.raw(this, prop, defaultType);
        }
        remove() {
          if (this.parent) {
            this.parent.removeChild(this);
          }
          this.parent = void 0;
          return this;
        }
        replaceWith(...nodes) {
          if (this.parent) {
            let bookmark = this;
            let foundSelf = false;
            for (let node of nodes) {
              if (node === this) {
                foundSelf = true;
              } else if (foundSelf) {
                this.parent.insertAfter(bookmark, node);
                bookmark = node;
              } else {
                this.parent.insertBefore(bookmark, node);
              }
            }
            if (!foundSelf) {
              this.remove();
            }
          }
          return this;
        }
        root() {
          let result = this;
          while (result.parent && result.parent.type !== "document") {
            result = result.parent;
          }
          return result;
        }
        toJSON(_, inputs) {
          let fixed = {};
          let emitInputs = inputs == null;
          inputs = inputs || /* @__PURE__ */ new Map();
          let inputsNextIndex = 0;
          for (let name in this) {
            if (!Object.prototype.hasOwnProperty.call(this, name)) {
              continue;
            }
            if (name === "parent" || name === "proxyCache") continue;
            let value = this[name];
            if (Array.isArray(value)) {
              fixed[name] = value.map((i) => {
                if (typeof i === "object" && i.toJSON) {
                  return i.toJSON(null, inputs);
                } else {
                  return i;
                }
              });
            } else if (typeof value === "object" && value.toJSON) {
              fixed[name] = value.toJSON(null, inputs);
            } else if (name === "source") {
              if (value == null) continue;
              let inputId = inputs.get(value.input);
              if (inputId == null) {
                inputId = inputsNextIndex;
                inputs.set(value.input, inputsNextIndex);
                inputsNextIndex++;
              }
              fixed[name] = {
                end: value.end,
                inputId,
                start: value.start
              };
            } else {
              fixed[name] = value;
            }
          }
          if (emitInputs) {
            fixed.inputs = [...inputs.keys()].map((input) => input.toJSON());
          }
          return fixed;
        }
        toProxy() {
          if (!this.proxyCache) {
            this.proxyCache = new Proxy(this, this.getProxyProcessor());
          }
          return this.proxyCache;
        }
        toString(stringifier = stringify2) {
          if (stringifier.stringify) stringifier = stringifier.stringify;
          let result = "";
          stringifier(this, (i) => {
            result += i;
          });
          return result;
        }
        warn(result, text, opts = {}) {
          let data = { node: this };
          for (let i in opts) data[i] = opts[i];
          return result.warn(text, data);
        }
      };
      module.exports = Node3;
      Node3.default = Node3;
    }
  });

  // node_modules/postcss/lib/comment.js
  var require_comment = __commonJS({
    "node_modules/postcss/lib/comment.js"(exports, module) {
      "use strict";
      var Node3 = require_node();
      var Comment2 = class extends Node3 {
        constructor(defaults2) {
          super(defaults2);
          this.type = "comment";
        }
      };
      module.exports = Comment2;
      Comment2.default = Comment2;
    }
  });

  // node_modules/postcss/lib/declaration.js
  var require_declaration = __commonJS({
    "node_modules/postcss/lib/declaration.js"(exports, module) {
      "use strict";
      var Node3 = require_node();
      var Declaration2 = class extends Node3 {
        get variable() {
          return this.prop.startsWith("--") || this.prop[0] === "$";
        }
        constructor(defaults2) {
          if (defaults2 && typeof defaults2.value !== "undefined" && typeof defaults2.value !== "string") {
            defaults2 = { ...defaults2, value: String(defaults2.value) };
          }
          super(defaults2);
          this.type = "decl";
        }
      };
      module.exports = Declaration2;
      Declaration2.default = Declaration2;
    }
  });

  // node_modules/postcss/lib/container.js
  var require_container = __commonJS({
    "node_modules/postcss/lib/container.js"(exports, module) {
      "use strict";
      var Comment2 = require_comment();
      var Declaration2 = require_declaration();
      var Node3 = require_node();
      var { isClean, my } = require_symbols();
      var AtRule2;
      var parse3;
      var Root2;
      var Rule2;
      function cleanSource(nodes) {
        return nodes.map((i) => {
          if (i.nodes) i.nodes = cleanSource(i.nodes);
          delete i.source;
          return i;
        });
      }
      function markTreeDirty(node) {
        node[isClean] = false;
        if (node.proxyOf.nodes) {
          for (let i of node.proxyOf.nodes) {
            markTreeDirty(i);
          }
        }
      }
      var Container2 = class _Container extends Node3 {
        get first() {
          if (!this.proxyOf.nodes) return void 0;
          return this.proxyOf.nodes[0];
        }
        get last() {
          if (!this.proxyOf.nodes) return void 0;
          return this.proxyOf.nodes[this.proxyOf.nodes.length - 1];
        }
        append(...children) {
          for (let child of children) {
            let nodes = this.normalize(child, this.last);
            for (let node of nodes) this.proxyOf.nodes.push(node);
          }
          this.markDirty();
          return this;
        }
        cleanRaws(keepBetween) {
          super.cleanRaws(keepBetween);
          if (this.nodes) {
            for (let node of this.nodes) node.cleanRaws(keepBetween);
          }
        }
        each(callback) {
          if (!this.proxyOf.nodes) return void 0;
          let iterator = this.getIterator();
          let index, result;
          while (this.indexes[iterator] < this.proxyOf.nodes.length) {
            index = this.indexes[iterator];
            result = callback(this.proxyOf.nodes[index], index);
            if (result === false) break;
            this.indexes[iterator] += 1;
          }
          delete this.indexes[iterator];
          return result;
        }
        every(condition) {
          return this.nodes.every(condition);
        }
        getIterator() {
          if (!this.lastEach) this.lastEach = 0;
          if (!this.indexes) this.indexes = {};
          this.lastEach += 1;
          let iterator = this.lastEach;
          this.indexes[iterator] = 0;
          return iterator;
        }
        getProxyProcessor() {
          return {
            get(node, prop) {
              if (prop === "proxyOf") {
                return node;
              } else if (!node[prop]) {
                return node[prop];
              } else if (prop === "each" || typeof prop === "string" && prop.startsWith("walk")) {
                return (...args) => {
                  return node[prop](
                    ...args.map((i) => {
                      if (typeof i === "function") {
                        return (child, index) => i(child.toProxy(), index);
                      } else {
                        return i;
                      }
                    })
                  );
                };
              } else if (prop === "every" || prop === "some") {
                return (cb) => {
                  return node[prop](
                    (child, ...other) => cb(child.toProxy(), ...other)
                  );
                };
              } else if (prop === "root") {
                return () => node.root().toProxy();
              } else if (prop === "nodes") {
                return node.nodes.map((i) => i.toProxy());
              } else if (prop === "first" || prop === "last") {
                return node[prop].toProxy();
              } else {
                return node[prop];
              }
            },
            set(node, prop, value) {
              if (node[prop] === value) return true;
              node[prop] = value;
              if (prop === "name" || prop === "params" || prop === "selector") {
                node.markDirty();
              }
              return true;
            }
          };
        }
        index(child) {
          if (typeof child === "number") return child;
          if (child.proxyOf) child = child.proxyOf;
          return this.proxyOf.nodes.indexOf(child);
        }
        insertAfter(exist, add) {
          let existIndex = this.index(exist);
          let nodes = this.normalize(add, this.proxyOf.nodes[existIndex]).reverse();
          existIndex = this.index(exist);
          for (let node of nodes) this.proxyOf.nodes.splice(existIndex + 1, 0, node);
          let index;
          for (let id in this.indexes) {
            index = this.indexes[id];
            if (existIndex < index) {
              this.indexes[id] = index + nodes.length;
            }
          }
          this.markDirty();
          return this;
        }
        insertBefore(exist, add) {
          let existIndex = this.index(exist);
          let type = existIndex === 0 ? "prepend" : false;
          let nodes = this.normalize(
            add,
            this.proxyOf.nodes[existIndex],
            type
          ).reverse();
          existIndex = this.index(exist);
          for (let node of nodes) this.proxyOf.nodes.splice(existIndex, 0, node);
          let index;
          for (let id in this.indexes) {
            index = this.indexes[id];
            if (existIndex <= index) {
              this.indexes[id] = index + nodes.length;
            }
          }
          this.markDirty();
          return this;
        }
        normalize(nodes, sample) {
          if (typeof nodes === "string") {
            nodes = cleanSource(parse3(nodes).nodes);
          } else if (typeof nodes === "undefined") {
            nodes = [];
          } else if (Array.isArray(nodes)) {
            nodes = nodes.slice(0);
            for (let i of nodes) {
              if (i.parent) i.parent.removeChild(i, "ignore");
            }
          } else if (nodes.type === "root" && this.type !== "document") {
            nodes = nodes.nodes.slice(0);
            for (let i of nodes) {
              if (i.parent) i.parent.removeChild(i, "ignore");
            }
          } else if (nodes.type) {
            nodes = [nodes];
          } else if (nodes.prop) {
            if (typeof nodes.value === "undefined") {
              throw new Error("Value field is missed in node creation");
            } else if (typeof nodes.value !== "string") {
              nodes.value = String(nodes.value);
            }
            nodes = [new Declaration2(nodes)];
          } else if (nodes.selector || nodes.selectors) {
            nodes = [new Rule2(nodes)];
          } else if (nodes.name) {
            nodes = [new AtRule2(nodes)];
          } else if (nodes.text) {
            nodes = [new Comment2(nodes)];
          } else {
            throw new Error("Unknown node type in node creation");
          }
          let processed = nodes.map((i) => {
            if (!i[my]) _Container.rebuild(i);
            i = i.proxyOf;
            if (i.parent) i.parent.removeChild(i);
            if (i[isClean]) markTreeDirty(i);
            if (!i.raws) i.raws = {};
            if (typeof i.raws.before === "undefined") {
              if (sample && typeof sample.raws.before !== "undefined") {
                i.raws.before = sample.raws.before.replace(/\S/g, "");
              }
            }
            i.parent = this.proxyOf;
            return i;
          });
          return processed;
        }
        prepend(...children) {
          children = children.reverse();
          for (let child of children) {
            let nodes = this.normalize(child, this.first, "prepend").reverse();
            for (let node of nodes) this.proxyOf.nodes.unshift(node);
            for (let id in this.indexes) {
              this.indexes[id] = this.indexes[id] + nodes.length;
            }
          }
          this.markDirty();
          return this;
        }
        push(child) {
          child.parent = this;
          this.proxyOf.nodes.push(child);
          return this;
        }
        removeAll() {
          for (let node of this.proxyOf.nodes) node.parent = void 0;
          this.proxyOf.nodes = [];
          this.markDirty();
          return this;
        }
        removeChild(child) {
          child = this.index(child);
          this.proxyOf.nodes[child].parent = void 0;
          this.proxyOf.nodes.splice(child, 1);
          let index;
          for (let id in this.indexes) {
            index = this.indexes[id];
            if (index >= child) {
              this.indexes[id] = index - 1;
            }
          }
          this.markDirty();
          return this;
        }
        replaceValues(pattern, opts, callback) {
          if (!callback) {
            callback = opts;
            opts = {};
          }
          this.walkDecls((decl2) => {
            if (opts.props && !opts.props.includes(decl2.prop)) return;
            if (opts.fast && !decl2.value.includes(opts.fast)) return;
            decl2.value = decl2.value.replace(pattern, callback);
          });
          this.markDirty();
          return this;
        }
        some(condition) {
          return this.nodes.some(condition);
        }
        walk(callback) {
          return this.each((child, i) => {
            let result;
            try {
              result = callback(child, i);
            } catch (e) {
              throw child.addToError(e);
            }
            if (result !== false && child.walk) {
              result = child.walk(callback);
            }
            return result;
          });
        }
        walkAtRules(name, callback) {
          if (!callback) {
            callback = name;
            return this.walk((child, i) => {
              if (child.type === "atrule") {
                return callback(child, i);
              }
            });
          }
          if (name instanceof RegExp) {
            return this.walk((child, i) => {
              if (child.type === "atrule" && name.test(child.name)) {
                return callback(child, i);
              }
            });
          }
          return this.walk((child, i) => {
            if (child.type === "atrule" && child.name === name) {
              return callback(child, i);
            }
          });
        }
        walkComments(callback) {
          return this.walk((child, i) => {
            if (child.type === "comment") {
              return callback(child, i);
            }
          });
        }
        walkDecls(prop, callback) {
          if (!callback) {
            callback = prop;
            return this.walk((child, i) => {
              if (child.type === "decl") {
                return callback(child, i);
              }
            });
          }
          if (prop instanceof RegExp) {
            return this.walk((child, i) => {
              if (child.type === "decl" && prop.test(child.prop)) {
                return callback(child, i);
              }
            });
          }
          return this.walk((child, i) => {
            if (child.type === "decl" && child.prop === prop) {
              return callback(child, i);
            }
          });
        }
        walkRules(selector, callback) {
          if (!callback) {
            callback = selector;
            return this.walk((child, i) => {
              if (child.type === "rule") {
                return callback(child, i);
              }
            });
          }
          if (selector instanceof RegExp) {
            return this.walk((child, i) => {
              if (child.type === "rule" && selector.test(child.selector)) {
                return callback(child, i);
              }
            });
          }
          return this.walk((child, i) => {
            if (child.type === "rule" && child.selector === selector) {
              return callback(child, i);
            }
          });
        }
      };
      Container2.registerParse = (dependant) => {
        parse3 = dependant;
      };
      Container2.registerRule = (dependant) => {
        Rule2 = dependant;
      };
      Container2.registerAtRule = (dependant) => {
        AtRule2 = dependant;
      };
      Container2.registerRoot = (dependant) => {
        Root2 = dependant;
      };
      module.exports = Container2;
      Container2.default = Container2;
      Container2.rebuild = (node) => {
        if (node.type === "atrule") {
          Object.setPrototypeOf(node, AtRule2.prototype);
        } else if (node.type === "rule") {
          Object.setPrototypeOf(node, Rule2.prototype);
        } else if (node.type === "decl") {
          Object.setPrototypeOf(node, Declaration2.prototype);
        } else if (node.type === "comment") {
          Object.setPrototypeOf(node, Comment2.prototype);
        } else if (node.type === "root") {
          Object.setPrototypeOf(node, Root2.prototype);
        }
        node[my] = true;
        if (node.nodes) {
          node.nodes.forEach((child) => {
            Container2.rebuild(child);
          });
        }
      };
    }
  });

  // node_modules/postcss/lib/at-rule.js
  var require_at_rule = __commonJS({
    "node_modules/postcss/lib/at-rule.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var AtRule2 = class extends Container2 {
        constructor(defaults2) {
          super(defaults2);
          this.type = "atrule";
        }
        append(...children) {
          if (!this.proxyOf.nodes) this.nodes = [];
          return super.append(...children);
        }
        prepend(...children) {
          if (!this.proxyOf.nodes) this.nodes = [];
          return super.prepend(...children);
        }
      };
      module.exports = AtRule2;
      AtRule2.default = AtRule2;
      Container2.registerAtRule(AtRule2);
    }
  });

  // node_modules/postcss/lib/document.js
  var require_document = __commonJS({
    "node_modules/postcss/lib/document.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var LazyResult;
      var Processor2;
      var Document2 = class extends Container2 {
        constructor(defaults2) {
          super({ type: "document", ...defaults2 });
          if (!this.nodes) {
            this.nodes = [];
          }
        }
        toResult(opts = {}) {
          let lazy = new LazyResult(new Processor2(), this, opts);
          return lazy.stringify();
        }
      };
      Document2.registerLazyResult = (dependant) => {
        LazyResult = dependant;
      };
      Document2.registerProcessor = (dependant) => {
        Processor2 = dependant;
      };
      module.exports = Document2;
      Document2.default = Document2;
    }
  });

  // node_modules/nanoid/non-secure/index.cjs
  var require_non_secure = __commonJS({
    "node_modules/nanoid/non-secure/index.cjs"(exports, module) {
      var urlAlphabet = "useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict";
      var customAlphabet = (alphabet, defaultSize = 21) => {
        return (size = defaultSize) => {
          let id = "";
          let i = size | 0;
          while (i--) {
            id += alphabet[Math.random() * alphabet.length | 0];
          }
          return id;
        };
      };
      var nanoid = (size = 21) => {
        let id = "";
        let i = size | 0;
        while (i--) {
          id += urlAlphabet[Math.random() * 64 | 0];
        }
        return id;
      };
      module.exports = { nanoid, customAlphabet };
    }
  });

  // (disabled):path
  var require_path = __commonJS({
    "(disabled):path"() {
    }
  });

  // (disabled):node_modules/source-map-js/source-map.js
  var require_source_map = __commonJS({
    "(disabled):node_modules/source-map-js/source-map.js"() {
    }
  });

  // (disabled):url
  var require_url = __commonJS({
    "(disabled):url"() {
    }
  });

  // (disabled):fs
  var require_fs = __commonJS({
    "(disabled):fs"() {
    }
  });

  // node_modules/postcss/lib/previous-map.js
  var require_previous_map = __commonJS({
    "node_modules/postcss/lib/previous-map.js"(exports, module) {
      "use strict";
      var { existsSync, readFileSync } = require_fs();
      var { dirname, join } = require_path();
      var { SourceMapConsumer, SourceMapGenerator } = require_source_map();
      function fromBase64(str) {
        if (Buffer) {
          return Buffer.from(str, "base64").toString();
        } else {
          return window.atob(str);
        }
      }
      var PreviousMap = class {
        constructor(css, opts) {
          if (opts.map === false) return;
          this.loadAnnotation(css);
          this.inline = this.startWith(this.annotation, "data:");
          let prev = opts.map ? opts.map.prev : void 0;
          let text = this.loadMap(opts.from, prev);
          if (!this.mapFile && opts.from) {
            this.mapFile = opts.from;
          }
          if (this.mapFile) this.root = dirname(this.mapFile);
          if (text) this.text = text;
        }
        consumer() {
          if (!this.consumerCache) {
            this.consumerCache = new SourceMapConsumer(this.text);
          }
          return this.consumerCache;
        }
        decodeInline(text) {
          let baseCharsetUri = /^data:application\/json;charset=utf-?8;base64,/;
          let baseUri = /^data:application\/json;base64,/;
          let charsetUri = /^data:application\/json;charset=utf-?8,/;
          let uri = /^data:application\/json,/;
          let uriMatch = text.match(charsetUri) || text.match(uri);
          if (uriMatch) {
            return decodeURIComponent(text.substr(uriMatch[0].length));
          }
          let baseUriMatch = text.match(baseCharsetUri) || text.match(baseUri);
          if (baseUriMatch) {
            return fromBase64(text.substr(baseUriMatch[0].length));
          }
          let encoding = text.match(/data:application\/json;([^,]+),/)[1];
          throw new Error("Unsupported source map encoding " + encoding);
        }
        getAnnotationURL(sourceMapString) {
          return sourceMapString.replace(/^\/\*\s*# sourceMappingURL=/, "").trim();
        }
        isMap(map) {
          if (typeof map !== "object") return false;
          return typeof map.mappings === "string" || typeof map._mappings === "string" || Array.isArray(map.sections);
        }
        loadAnnotation(css) {
          let comments = css.match(/\/\*\s*# sourceMappingURL=/g);
          if (!comments) return;
          let start = css.lastIndexOf(comments.pop());
          let end = css.indexOf("*/", start);
          if (start > -1 && end > -1) {
            this.annotation = this.getAnnotationURL(css.substring(start, end));
          }
        }
        loadFile(path) {
          this.root = dirname(path);
          if (existsSync(path)) {
            this.mapFile = path;
            return readFileSync(path, "utf-8").toString().trim();
          }
        }
        loadMap(file, prev) {
          if (prev === false) return false;
          if (prev) {
            if (typeof prev === "string") {
              return prev;
            } else if (typeof prev === "function") {
              let prevPath = prev(file);
              if (prevPath) {
                let map = this.loadFile(prevPath);
                if (!map) {
                  throw new Error(
                    "Unable to load previous source map: " + prevPath.toString()
                  );
                }
                return map;
              }
            } else if (prev instanceof SourceMapConsumer) {
              return SourceMapGenerator.fromSourceMap(prev).toString();
            } else if (prev instanceof SourceMapGenerator) {
              return prev.toString();
            } else if (this.isMap(prev)) {
              return JSON.stringify(prev);
            } else {
              throw new Error(
                "Unsupported previous source map format: " + prev.toString()
              );
            }
          } else if (this.inline) {
            return this.decodeInline(this.annotation);
          } else if (this.annotation) {
            let map = this.annotation;
            if (file) map = join(dirname(file), map);
            return this.loadFile(map);
          }
        }
        startWith(string, start) {
          if (!string) return false;
          return string.substr(0, start.length) === start;
        }
        withContent() {
          return !!(this.consumer().sourcesContent && this.consumer().sourcesContent.length > 0);
        }
      };
      module.exports = PreviousMap;
      PreviousMap.default = PreviousMap;
    }
  });

  // node_modules/postcss/lib/input.js
  var require_input = __commonJS({
    "node_modules/postcss/lib/input.js"(exports, module) {
      "use strict";
      var { nanoid } = require_non_secure();
      var { isAbsolute, resolve } = require_path();
      var { SourceMapConsumer, SourceMapGenerator } = require_source_map();
      var { fileURLToPath, pathToFileURL } = require_url();
      var CssSyntaxError2 = require_css_syntax_error();
      var PreviousMap = require_previous_map();
      var terminalHighlight = require_terminal_highlight();
      var lineToIndexCache = Symbol("lineToIndexCache");
      var sourceMapAvailable = Boolean(SourceMapConsumer && SourceMapGenerator);
      var pathAvailable = Boolean(resolve && isAbsolute);
      function getLineToIndex(input) {
        if (input[lineToIndexCache]) return input[lineToIndexCache];
        let lines = input.css.split("\n");
        let lineToIndex = new Array(lines.length);
        let prevIndex = 0;
        for (let i = 0, l = lines.length; i < l; i++) {
          lineToIndex[i] = prevIndex;
          prevIndex += lines[i].length + 1;
        }
        input[lineToIndexCache] = lineToIndex;
        return lineToIndex;
      }
      var Input2 = class {
        get from() {
          return this.file || this.id;
        }
        constructor(css, opts = {}) {
          if (css === null || typeof css === "undefined" || typeof css === "object" && !css.toString) {
            throw new Error(`PostCSS received ${css} instead of CSS string`);
          }
          this.css = css.toString();
          if (this.css[0] === "\uFEFF" || this.css[0] === "\uFFFE") {
            this.hasBOM = true;
            this.css = this.css.slice(1);
          } else {
            this.hasBOM = false;
          }
          this.document = this.css;
          if (opts.document) this.document = opts.document.toString();
          if (opts.from) {
            if (!pathAvailable || /^\w+:\/\//.test(opts.from) || isAbsolute(opts.from)) {
              this.file = opts.from;
            } else {
              this.file = resolve(opts.from);
            }
          }
          if (pathAvailable && sourceMapAvailable) {
            let map = new PreviousMap(this.css, opts);
            if (map.text) {
              this.map = map;
              let file = map.consumer().file;
              if (!this.file && file) this.file = this.mapResolve(file);
            }
          }
          if (!this.file) {
            this.id = "<input css " + nanoid(6) + ">";
          }
          if (this.map) this.map.file = this.from;
        }
        error(message, line, column, opts = {}) {
          let endColumn, endLine, endOffset, offset, result;
          if (line && typeof line === "object") {
            let start = line;
            let end = column;
            if (typeof start.offset === "number") {
              offset = start.offset;
              let pos = this.fromOffset(offset);
              line = pos.line;
              column = pos.col;
            } else {
              line = start.line;
              column = start.column;
              offset = this.fromLineAndColumn(line, column);
            }
            if (typeof end.offset === "number") {
              endOffset = end.offset;
              let pos = this.fromOffset(endOffset);
              endLine = pos.line;
              endColumn = pos.col;
            } else {
              endLine = end.line;
              endColumn = end.column;
              endOffset = this.fromLineAndColumn(end.line, end.column);
            }
          } else if (!column) {
            offset = line;
            let pos = this.fromOffset(offset);
            line = pos.line;
            column = pos.col;
          } else {
            offset = this.fromLineAndColumn(line, column);
          }
          let origin = this.origin(line, column, endLine, endColumn);
          if (origin) {
            result = new CssSyntaxError2(
              message,
              origin.endLine === void 0 ? origin.line : { column: origin.column, line: origin.line },
              origin.endLine === void 0 ? origin.column : { column: origin.endColumn, line: origin.endLine },
              origin.source,
              origin.file,
              opts.plugin
            );
          } else {
            result = new CssSyntaxError2(
              message,
              endLine === void 0 ? line : { column, line },
              endLine === void 0 ? column : { column: endColumn, line: endLine },
              this.css,
              this.file,
              opts.plugin
            );
          }
          result.input = { column, endColumn, endLine, endOffset, line, offset, source: this.css };
          if (this.file) {
            if (pathToFileURL) {
              result.input.url = pathToFileURL(this.file).toString();
            }
            result.input.file = this.file;
          }
          return result;
        }
        fromLineAndColumn(line, column) {
          let lineToIndex = getLineToIndex(this);
          let index = lineToIndex[line - 1];
          return index + column - 1;
        }
        fromOffset(offset) {
          let lineToIndex = getLineToIndex(this);
          let lastLine = lineToIndex[lineToIndex.length - 1];
          let min = 0;
          if (offset >= lastLine) {
            min = lineToIndex.length - 1;
          } else {
            let max = lineToIndex.length - 2;
            let mid;
            while (min < max) {
              mid = min + (max - min >> 1);
              if (offset < lineToIndex[mid]) {
                max = mid - 1;
              } else if (offset >= lineToIndex[mid + 1]) {
                min = mid + 1;
              } else {
                min = mid;
                break;
              }
            }
          }
          return {
            col: offset - lineToIndex[min] + 1,
            line: min + 1
          };
        }
        mapResolve(file) {
          if (/^\w+:\/\//.test(file)) {
            return file;
          }
          return resolve(this.map.consumer().sourceRoot || this.map.root || ".", file);
        }
        origin(line, column, endLine, endColumn) {
          if (!this.map) return false;
          let consumer = this.map.consumer();
          let from = consumer.originalPositionFor({ column, line });
          if (!from.source) return false;
          let to;
          if (typeof endLine === "number") {
            to = consumer.originalPositionFor({ column: endColumn, line: endLine });
          }
          let fromUrl;
          if (isAbsolute(from.source)) {
            fromUrl = pathToFileURL(from.source);
          } else {
            fromUrl = new URL(
              from.source,
              this.map.consumer().sourceRoot || pathToFileURL(this.map.mapFile)
            );
          }
          let result = {
            column: from.column,
            endColumn: to && to.column,
            endLine: to && to.line,
            line: from.line,
            url: fromUrl.toString()
          };
          if (fromUrl.protocol === "file:") {
            if (fileURLToPath) {
              result.file = fileURLToPath(fromUrl);
            } else {
              throw new Error(`file: protocol is not available in this PostCSS build`);
            }
          }
          let source = consumer.sourceContentFor(from.source);
          if (source) result.source = source;
          return result;
        }
        toJSON() {
          let json = {};
          for (let name of ["hasBOM", "css", "file", "id"]) {
            if (this[name] != null) {
              json[name] = this[name];
            }
          }
          if (this.map) {
            json.map = { ...this.map };
            if (json.map.consumerCache) {
              json.map.consumerCache = void 0;
            }
          }
          return json;
        }
      };
      module.exports = Input2;
      Input2.default = Input2;
      if (terminalHighlight && terminalHighlight.registerInput) {
        terminalHighlight.registerInput(Input2);
      }
    }
  });

  // node_modules/postcss/lib/root.js
  var require_root = __commonJS({
    "node_modules/postcss/lib/root.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var LazyResult;
      var Processor2;
      var Root2 = class extends Container2 {
        constructor(defaults2) {
          super(defaults2);
          this.type = "root";
          if (!this.nodes) this.nodes = [];
        }
        normalize(child, sample, type) {
          let nodes = super.normalize(child);
          if (sample) {
            if (type === "prepend") {
              if (this.nodes.length > 1) {
                sample.raws.before = this.nodes[1].raws.before;
              } else {
                delete sample.raws.before;
              }
            } else if (this.first !== sample) {
              for (let node of nodes) {
                node.raws.before = sample.raws.before;
              }
            }
          }
          return nodes;
        }
        removeChild(child, ignore) {
          let index = this.index(child);
          if (!ignore && index === 0 && this.nodes.length > 1) {
            this.nodes[1].raws.before = this.nodes[index].raws.before;
          }
          return super.removeChild(child);
        }
        toResult(opts = {}) {
          let lazy = new LazyResult(new Processor2(), this, opts);
          return lazy.stringify();
        }
      };
      Root2.registerLazyResult = (dependant) => {
        LazyResult = dependant;
      };
      Root2.registerProcessor = (dependant) => {
        Processor2 = dependant;
      };
      module.exports = Root2;
      Root2.default = Root2;
      Container2.registerRoot(Root2);
    }
  });

  // node_modules/postcss/lib/list.js
  var require_list = __commonJS({
    "node_modules/postcss/lib/list.js"(exports, module) {
      "use strict";
      var list2 = {
        comma(string) {
          return list2.split(string, [","], true);
        },
        space(string) {
          let spaces = [" ", "\n", "	"];
          return list2.split(string, spaces);
        },
        split(string, separators, last) {
          let array = [];
          let current = "";
          let split = false;
          let func = 0;
          let inQuote = false;
          let prevQuote = "";
          let escape = false;
          for (let letter of string) {
            if (escape) {
              escape = false;
            } else if (letter === "\\") {
              escape = true;
            } else if (inQuote) {
              if (letter === prevQuote) {
                inQuote = false;
              }
            } else if (letter === '"' || letter === "'") {
              inQuote = true;
              prevQuote = letter;
            } else if (letter === "(") {
              func += 1;
            } else if (letter === ")") {
              if (func > 0) func -= 1;
            } else if (func === 0) {
              if (separators.includes(letter)) split = true;
            }
            if (split) {
              if (current !== "") array.push(current.trim());
              current = "";
              split = false;
            } else {
              current += letter;
            }
          }
          if (last || current !== "") array.push(current.trim());
          return array;
        }
      };
      module.exports = list2;
      list2.default = list2;
    }
  });

  // node_modules/postcss/lib/rule.js
  var require_rule = __commonJS({
    "node_modules/postcss/lib/rule.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var list2 = require_list();
      var Rule2 = class extends Container2 {
        get selectors() {
          return list2.comma(this.selector);
        }
        set selectors(values) {
          let match = this.selector ? this.selector.match(/,\s*/) : null;
          let sep = match ? match[0] : "," + this.raw("between", "beforeOpen");
          this.selector = values.join(sep);
        }
        constructor(defaults2) {
          super(defaults2);
          this.type = "rule";
          if (!this.nodes) this.nodes = [];
        }
      };
      module.exports = Rule2;
      Rule2.default = Rule2;
      Container2.registerRule(Rule2);
    }
  });

  // node_modules/postcss/lib/fromJSON.js
  var require_fromJSON = __commonJS({
    "node_modules/postcss/lib/fromJSON.js"(exports, module) {
      "use strict";
      var AtRule2 = require_at_rule();
      var Comment2 = require_comment();
      var Declaration2 = require_declaration();
      var Input2 = require_input();
      var PreviousMap = require_previous_map();
      var Root2 = require_root();
      var Rule2 = require_rule();
      function fromJSON2(json, inputs) {
        if (Array.isArray(json)) return json.map((n) => fromJSON2(n));
        let { inputs: ownInputs, ...defaults2 } = json;
        if (ownInputs) {
          inputs = [];
          for (let input of ownInputs) {
            let inputHydrated = { ...input, __proto__: Input2.prototype };
            if (inputHydrated.map) {
              inputHydrated.map = {
                ...inputHydrated.map,
                __proto__: PreviousMap.prototype
              };
            }
            inputs.push(inputHydrated);
          }
        }
        if (defaults2.nodes) {
          defaults2.nodes = json.nodes.map((n) => fromJSON2(n, inputs));
        }
        if (defaults2.source) {
          let { inputId, ...source } = defaults2.source;
          defaults2.source = source;
          if (inputId != null) {
            defaults2.source.input = inputs[inputId];
          }
        }
        if (defaults2.type === "root") {
          return new Root2(defaults2);
        } else if (defaults2.type === "decl") {
          return new Declaration2(defaults2);
        } else if (defaults2.type === "rule") {
          return new Rule2(defaults2);
        } else if (defaults2.type === "comment") {
          return new Comment2(defaults2);
        } else if (defaults2.type === "atrule") {
          return new AtRule2(defaults2);
        } else {
          throw new Error("Unknown node type: " + json.type);
        }
      }
      module.exports = fromJSON2;
      fromJSON2.default = fromJSON2;
    }
  });

  // node_modules/postcss/lib/map-generator.js
  var require_map_generator = __commonJS({
    "node_modules/postcss/lib/map-generator.js"(exports, module) {
      "use strict";
      var { dirname, relative, resolve, sep } = require_path();
      var { SourceMapConsumer, SourceMapGenerator } = require_source_map();
      var { pathToFileURL } = require_url();
      var Input2 = require_input();
      var sourceMapAvailable = Boolean(SourceMapConsumer && SourceMapGenerator);
      var pathAvailable = Boolean(dirname && resolve && relative && sep);
      var MapGenerator = class {
        constructor(stringify2, root2, opts, cssString) {
          this.stringify = stringify2;
          this.mapOpts = opts.map || {};
          this.root = root2;
          this.opts = opts;
          this.css = cssString;
          this.originalCSS = cssString;
          this.usesFileUrls = !this.mapOpts.from && this.mapOpts.absolute;
          this.memoizedFileURLs = /* @__PURE__ */ new Map();
          this.memoizedPaths = /* @__PURE__ */ new Map();
          this.memoizedURLs = /* @__PURE__ */ new Map();
        }
        addAnnotation() {
          let content;
          if (this.isInline()) {
            content = "data:application/json;base64," + this.toBase64(this.map.toString());
          } else if (typeof this.mapOpts.annotation === "string") {
            content = this.mapOpts.annotation;
          } else if (typeof this.mapOpts.annotation === "function") {
            content = this.mapOpts.annotation(this.opts.to, this.root);
          } else {
            content = this.outputFile() + ".map";
          }
          let eol = "\n";
          if (this.css.includes("\r\n")) eol = "\r\n";
          this.css += eol + "/*# sourceMappingURL=" + content + " */";
        }
        applyPrevMaps() {
          for (let prev of this.previous()) {
            let from = this.toUrl(this.path(prev.file));
            let root2 = prev.root || dirname(prev.file);
            let map;
            if (this.mapOpts.sourcesContent === false) {
              map = new SourceMapConsumer(prev.text);
              if (map.sourcesContent) {
                map.sourcesContent = null;
              }
            } else {
              map = prev.consumer();
            }
            this.map.applySourceMap(map, from, this.toUrl(this.path(root2)));
          }
        }
        clearAnnotation() {
          if (this.mapOpts.annotation === false) return;
          if (this.root) {
            let node;
            for (let i = this.root.nodes.length - 1; i >= 0; i--) {
              node = this.root.nodes[i];
              if (node.type !== "comment") continue;
              if (node.text.startsWith("# sourceMappingURL=")) {
                this.root.removeChild(i);
              }
            }
          } else if (this.css) {
            this.css = this.css.replace(/\n*\/\*#[\S\s]*?\*\/$/gm, "");
          }
        }
        generate() {
          this.clearAnnotation();
          if (pathAvailable && sourceMapAvailable && this.isMap()) {
            return this.generateMap();
          } else {
            let result = "";
            this.stringify(this.root, (i) => {
              result += i;
            });
            return [result];
          }
        }
        generateMap() {
          if (this.root) {
            this.generateString();
          } else if (this.previous().length === 1) {
            let prev = this.previous()[0].consumer();
            prev.file = this.outputFile();
            this.map = SourceMapGenerator.fromSourceMap(prev, {
              ignoreInvalidMapping: true
            });
          } else {
            this.map = new SourceMapGenerator({
              file: this.outputFile(),
              ignoreInvalidMapping: true
            });
            this.map.addMapping({
              generated: { column: 0, line: 1 },
              original: { column: 0, line: 1 },
              source: this.opts.from ? this.toUrl(this.path(this.opts.from)) : "<no source>"
            });
          }
          if (this.isSourcesContent()) this.setSourcesContent();
          if (this.root && this.previous().length > 0) this.applyPrevMaps();
          if (this.isAnnotation()) this.addAnnotation();
          if (this.isInline()) {
            return [this.css];
          } else {
            return [this.css, this.map];
          }
        }
        generateString() {
          this.css = "";
          this.map = new SourceMapGenerator({
            file: this.outputFile(),
            ignoreInvalidMapping: true
          });
          let line = 1;
          let column = 1;
          let noSource = "<no source>";
          let mapping = {
            generated: { column: 0, line: 0 },
            original: { column: 0, line: 0 },
            source: ""
          };
          let last, lines;
          this.stringify(this.root, (str, node, type) => {
            this.css += str;
            if (node && type !== "end") {
              mapping.generated.line = line;
              mapping.generated.column = column - 1;
              if (node.source && node.source.start) {
                mapping.source = this.sourcePath(node);
                mapping.original.line = node.source.start.line;
                mapping.original.column = node.source.start.column - 1;
                this.map.addMapping(mapping);
              } else {
                mapping.source = noSource;
                mapping.original.line = 1;
                mapping.original.column = 0;
                this.map.addMapping(mapping);
              }
            }
            lines = str.match(/\n/g);
            if (lines) {
              line += lines.length;
              last = str.lastIndexOf("\n");
              column = str.length - last;
            } else {
              column += str.length;
            }
            if (node && type !== "start") {
              let p = node.parent || { raws: {} };
              let childless = node.type === "decl" || node.type === "atrule" && !node.nodes;
              if (!childless || node !== p.last || p.raws.semicolon) {
                if (node.source && node.source.end) {
                  mapping.source = this.sourcePath(node);
                  mapping.original.line = node.source.end.line;
                  mapping.original.column = node.source.end.column - 1;
                  mapping.generated.line = line;
                  mapping.generated.column = column - 2;
                  this.map.addMapping(mapping);
                } else {
                  mapping.source = noSource;
                  mapping.original.line = 1;
                  mapping.original.column = 0;
                  mapping.generated.line = line;
                  mapping.generated.column = column - 1;
                  this.map.addMapping(mapping);
                }
              }
            }
          });
        }
        isAnnotation() {
          if (this.isInline()) {
            return true;
          }
          if (typeof this.mapOpts.annotation !== "undefined") {
            return this.mapOpts.annotation;
          }
          if (this.previous().length) {
            return this.previous().some((i) => i.annotation);
          }
          return true;
        }
        isInline() {
          if (typeof this.mapOpts.inline !== "undefined") {
            return this.mapOpts.inline;
          }
          let annotation = this.mapOpts.annotation;
          if (typeof annotation !== "undefined" && annotation !== true) {
            return false;
          }
          if (this.previous().length) {
            return this.previous().some((i) => i.inline);
          }
          return true;
        }
        isMap() {
          if (typeof this.opts.map !== "undefined") {
            return !!this.opts.map;
          }
          return this.previous().length > 0;
        }
        isSourcesContent() {
          if (typeof this.mapOpts.sourcesContent !== "undefined") {
            return this.mapOpts.sourcesContent;
          }
          if (this.previous().length) {
            return this.previous().some((i) => i.withContent());
          }
          return true;
        }
        outputFile() {
          if (this.opts.to) {
            return this.path(this.opts.to);
          } else if (this.opts.from) {
            return this.path(this.opts.from);
          } else {
            return "to.css";
          }
        }
        path(file) {
          if (this.mapOpts.absolute) return file;
          if (file.charCodeAt(0) === 60) return file;
          if (/^\w+:\/\//.test(file)) return file;
          let cached = this.memoizedPaths.get(file);
          if (cached) return cached;
          let from = this.opts.to ? dirname(this.opts.to) : ".";
          if (typeof this.mapOpts.annotation === "string") {
            from = dirname(resolve(from, this.mapOpts.annotation));
          }
          let path = relative(from, file);
          this.memoizedPaths.set(file, path);
          return path;
        }
        previous() {
          if (!this.previousMaps) {
            this.previousMaps = [];
            if (this.root) {
              this.root.walk((node) => {
                if (node.source && node.source.input.map) {
                  let map = node.source.input.map;
                  if (!this.previousMaps.includes(map)) {
                    this.previousMaps.push(map);
                  }
                }
              });
            } else {
              let input = new Input2(this.originalCSS, this.opts);
              if (input.map) this.previousMaps.push(input.map);
            }
          }
          return this.previousMaps;
        }
        setSourcesContent() {
          let already = {};
          if (this.root) {
            this.root.walk((node) => {
              if (node.source) {
                let from = node.source.input.from;
                if (from && !already[from]) {
                  already[from] = true;
                  let fromUrl = this.usesFileUrls ? this.toFileUrl(from) : this.toUrl(this.path(from));
                  this.map.setSourceContent(fromUrl, node.source.input.css);
                }
              }
            });
          } else if (this.css) {
            let from = this.opts.from ? this.toUrl(this.path(this.opts.from)) : "<no source>";
            this.map.setSourceContent(from, this.css);
          }
        }
        sourcePath(node) {
          if (this.mapOpts.from) {
            return this.toUrl(this.mapOpts.from);
          } else if (this.usesFileUrls) {
            return this.toFileUrl(node.source.input.from);
          } else {
            return this.toUrl(this.path(node.source.input.from));
          }
        }
        toBase64(str) {
          if (Buffer) {
            return Buffer.from(str).toString("base64");
          } else {
            return window.btoa(unescape(encodeURIComponent(str)));
          }
        }
        toFileUrl(path) {
          let cached = this.memoizedFileURLs.get(path);
          if (cached) return cached;
          if (pathToFileURL) {
            let fileURL = pathToFileURL(path).toString();
            this.memoizedFileURLs.set(path, fileURL);
            return fileURL;
          } else {
            throw new Error(
              "`map.absolute` option is not available in this PostCSS build"
            );
          }
        }
        toUrl(path) {
          let cached = this.memoizedURLs.get(path);
          if (cached) return cached;
          if (sep === "\\") {
            path = path.replace(/\\/g, "/");
          }
          let url = encodeURI(path).replace(/[#?]/g, encodeURIComponent);
          this.memoizedURLs.set(path, url);
          return url;
        }
      };
      module.exports = MapGenerator;
    }
  });

  // node_modules/postcss/lib/tokenize.js
  var require_tokenize = __commonJS({
    "node_modules/postcss/lib/tokenize.js"(exports, module) {
      "use strict";
      var SINGLE_QUOTE = "'".charCodeAt(0);
      var DOUBLE_QUOTE = '"'.charCodeAt(0);
      var BACKSLASH = "\\".charCodeAt(0);
      var SLASH = "/".charCodeAt(0);
      var NEWLINE = "\n".charCodeAt(0);
      var SPACE = " ".charCodeAt(0);
      var FEED = "\f".charCodeAt(0);
      var TAB = "	".charCodeAt(0);
      var CR = "\r".charCodeAt(0);
      var OPEN_SQUARE = "[".charCodeAt(0);
      var CLOSE_SQUARE = "]".charCodeAt(0);
      var OPEN_PARENTHESES = "(".charCodeAt(0);
      var CLOSE_PARENTHESES = ")".charCodeAt(0);
      var OPEN_CURLY = "{".charCodeAt(0);
      var CLOSE_CURLY = "}".charCodeAt(0);
      var SEMICOLON = ";".charCodeAt(0);
      var ASTERISK = "*".charCodeAt(0);
      var COLON = ":".charCodeAt(0);
      var AT = "@".charCodeAt(0);
      var RE_AT_END = /[\t\n\f\r "#'()/;[\\\]{}]/g;
      var RE_WORD_END = /[\t\n\f\r !"#'():;@[\\\]{}]|\/(?=\*)/g;
      var RE_BAD_BRACKET = /.[\r\n"'(/\\]/;
      var RE_HEX_ESCAPE = /[\da-f]/i;
      module.exports = function tokenizer(input, options = {}) {
        let css = input.css.valueOf();
        let ignore = options.ignoreErrors;
        let code, content, escape, next, quote;
        let currentToken, escaped, escapePos, n, prev;
        let length = css.length;
        let pos = 0;
        let buffer = [];
        let returned = [];
        function position() {
          return pos;
        }
        function unclosed(what) {
          throw input.error("Unclosed " + what, pos);
        }
        function endOfFile() {
          return returned.length === 0 && pos >= length;
        }
        function nextToken(opts) {
          if (returned.length) return returned.pop();
          if (pos >= length) return;
          let ignoreUnclosed = opts ? opts.ignoreUnclosed : false;
          code = css.charCodeAt(pos);
          switch (code) {
            case NEWLINE:
            case SPACE:
            case TAB:
            case CR:
            case FEED: {
              next = pos;
              do {
                next += 1;
                code = css.charCodeAt(next);
              } while (code === SPACE || code === NEWLINE || code === TAB || code === CR || code === FEED);
              currentToken = ["space", css.slice(pos, next)];
              pos = next - 1;
              break;
            }
            case OPEN_SQUARE:
            case CLOSE_SQUARE:
            case OPEN_CURLY:
            case CLOSE_CURLY:
            case COLON:
            case SEMICOLON:
            case CLOSE_PARENTHESES: {
              let controlChar = String.fromCharCode(code);
              currentToken = [controlChar, controlChar, pos];
              break;
            }
            case OPEN_PARENTHESES: {
              prev = buffer.length ? buffer.pop()[1] : "";
              n = css.charCodeAt(pos + 1);
              if (prev === "url" && n !== SINGLE_QUOTE && n !== DOUBLE_QUOTE && n !== SPACE && n !== NEWLINE && n !== TAB && n !== FEED && n !== CR) {
                next = pos;
                do {
                  escaped = false;
                  next = css.indexOf(")", next + 1);
                  if (next === -1) {
                    if (ignore || ignoreUnclosed) {
                      next = pos;
                      break;
                    } else {
                      unclosed("bracket");
                    }
                  }
                  escapePos = next;
                  while (css.charCodeAt(escapePos - 1) === BACKSLASH) {
                    escapePos -= 1;
                    escaped = !escaped;
                  }
                } while (escaped);
                currentToken = ["brackets", css.slice(pos, next + 1), pos, next];
                pos = next;
              } else {
                next = css.indexOf(")", pos + 1);
                content = css.slice(pos, next + 1);
                if (next === -1 || RE_BAD_BRACKET.test(content)) {
                  currentToken = ["(", "(", pos];
                } else {
                  currentToken = ["brackets", content, pos, next];
                  pos = next;
                }
              }
              break;
            }
            case SINGLE_QUOTE:
            case DOUBLE_QUOTE: {
              quote = code === SINGLE_QUOTE ? "'" : '"';
              next = pos;
              do {
                escaped = false;
                next = css.indexOf(quote, next + 1);
                if (next === -1) {
                  if (ignore || ignoreUnclosed) {
                    next = pos + 1;
                    break;
                  } else {
                    unclosed("string");
                  }
                }
                escapePos = next;
                while (css.charCodeAt(escapePos - 1) === BACKSLASH) {
                  escapePos -= 1;
                  escaped = !escaped;
                }
              } while (escaped);
              currentToken = ["string", css.slice(pos, next + 1), pos, next];
              pos = next;
              break;
            }
            case AT: {
              RE_AT_END.lastIndex = pos + 1;
              RE_AT_END.test(css);
              if (RE_AT_END.lastIndex === 0) {
                next = css.length - 1;
              } else {
                next = RE_AT_END.lastIndex - 2;
              }
              currentToken = ["at-word", css.slice(pos, next + 1), pos, next];
              pos = next;
              break;
            }
            case BACKSLASH: {
              next = pos;
              escape = true;
              while (css.charCodeAt(next + 1) === BACKSLASH) {
                next += 1;
                escape = !escape;
              }
              code = css.charCodeAt(next + 1);
              if (escape && code !== SLASH && code !== SPACE && code !== NEWLINE && code !== TAB && code !== CR && code !== FEED) {
                next += 1;
                if (RE_HEX_ESCAPE.test(css.charAt(next))) {
                  while (RE_HEX_ESCAPE.test(css.charAt(next + 1))) {
                    next += 1;
                  }
                  if (css.charCodeAt(next + 1) === SPACE) {
                    next += 1;
                  }
                }
              }
              currentToken = ["word", css.slice(pos, next + 1), pos, next];
              pos = next;
              break;
            }
            default: {
              if (code === SLASH && css.charCodeAt(pos + 1) === ASTERISK) {
                next = css.indexOf("*/", pos + 2) + 1;
                if (next === 0) {
                  if (ignore || ignoreUnclosed) {
                    next = css.length;
                  } else {
                    unclosed("comment");
                  }
                }
                currentToken = ["comment", css.slice(pos, next + 1), pos, next];
                pos = next;
              } else {
                RE_WORD_END.lastIndex = pos + 1;
                RE_WORD_END.test(css);
                if (RE_WORD_END.lastIndex === 0) {
                  next = css.length - 1;
                } else {
                  next = RE_WORD_END.lastIndex - 2;
                }
                currentToken = ["word", css.slice(pos, next + 1), pos, next];
                buffer.push(currentToken);
                pos = next;
              }
              break;
            }
          }
          pos++;
          return currentToken;
        }
        function back(token) {
          returned.push(token);
        }
        return {
          back,
          endOfFile,
          nextToken,
          position
        };
      };
    }
  });

  // node_modules/postcss/lib/parser.js
  var require_parser = __commonJS({
    "node_modules/postcss/lib/parser.js"(exports, module) {
      "use strict";
      var AtRule2 = require_at_rule();
      var Comment2 = require_comment();
      var Declaration2 = require_declaration();
      var Root2 = require_root();
      var Rule2 = require_rule();
      var tokenizer = require_tokenize();
      var SAFE_COMMENT_NEIGHBOR = {
        empty: true,
        space: true
      };
      function findLastWithPosition(tokens) {
        for (let i = tokens.length - 1; i >= 0; i--) {
          let token = tokens[i];
          let pos = token[3] || token[2];
          if (pos) return pos;
        }
      }
      var Parser = class {
        constructor(input) {
          this.input = input;
          this.root = new Root2();
          this.current = this.root;
          this.spaces = "";
          this.semicolon = false;
          this.createTokenizer();
          this.root.source = { input, start: { column: 1, line: 1, offset: 0 } };
        }
        atrule(token) {
          let node = new AtRule2();
          node.name = token[1].slice(1);
          if (node.name === "") {
            this.unnamedAtrule(node, token);
          }
          this.init(node, token[2]);
          let type;
          let prev;
          let shift;
          let last = false;
          let open = false;
          let params = [];
          let brackets = [];
          while (!this.tokenizer.endOfFile()) {
            token = this.tokenizer.nextToken();
            type = token[0];
            if (type === "(" || type === "[") {
              brackets.push(type === "(" ? ")" : "]");
            } else if (type === "{" && brackets.length > 0) {
              brackets.push("}");
            } else if (type === brackets[brackets.length - 1]) {
              brackets.pop();
            }
            if (brackets.length === 0) {
              if (type === ";") {
                node.source.end = this.getPosition(token[2]);
                node.source.end.offset++;
                this.semicolon = true;
                break;
              } else if (type === "{") {
                open = true;
                break;
              } else if (type === "}") {
                if (params.length > 0) {
                  shift = params.length - 1;
                  prev = params[shift];
                  while (prev && prev[0] === "space") {
                    prev = params[--shift];
                  }
                  if (prev) {
                    node.source.end = this.getPosition(prev[3] || prev[2]);
                    node.source.end.offset++;
                  }
                }
                this.end(token);
                break;
              } else {
                params.push(token);
              }
            } else {
              params.push(token);
            }
            if (this.tokenizer.endOfFile()) {
              last = true;
              break;
            }
          }
          node.raws.between = this.spacesAndCommentsFromEnd(params);
          if (params.length) {
            node.raws.afterName = this.spacesAndCommentsFromStart(params);
            this.raw(node, "params", params);
            if (last) {
              token = params[params.length - 1];
              node.source.end = this.getPosition(token[3] || token[2]);
              node.source.end.offset++;
              this.spaces = node.raws.between;
              node.raws.between = "";
            }
          } else {
            node.raws.afterName = "";
            node.params = "";
          }
          if (open) {
            node.nodes = [];
            this.current = node;
          }
        }
        checkMissedSemicolon(tokens) {
          let colon = this.colon(tokens);
          if (colon === false) return;
          let founded = 0;
          let token;
          for (let j = colon - 1; j >= 0; j--) {
            token = tokens[j];
            if (token[0] !== "space") {
              founded += 1;
              if (founded === 2) break;
            }
          }
          throw this.input.error(
            "Missed semicolon",
            token[0] === "word" ? token[3] + 1 : token[2]
          );
        }
        colon(tokens) {
          let brackets = 0;
          let prev, token, type;
          for (let [i, element] of tokens.entries()) {
            token = element;
            type = token[0];
            if (type === "(") {
              brackets += 1;
            }
            if (type === ")") {
              brackets -= 1;
            }
            if (brackets === 0 && type === ":") {
              if (!prev) {
                this.doubleColon(token);
              } else if (prev[0] === "word" && prev[1] === "progid") {
                continue;
              } else {
                return i;
              }
            }
            prev = token;
          }
          return false;
        }
        comment(token) {
          let node = new Comment2();
          this.init(node, token[2]);
          node.source.end = this.getPosition(token[3] || token[2]);
          node.source.end.offset++;
          let text = token[1].slice(2, -2);
          if (/^\s*$/.test(text)) {
            node.text = "";
            node.raws.left = text;
            node.raws.right = "";
          } else {
            let match = text.match(/^(\s*)([^]*\S)(\s*)$/);
            node.text = match[2];
            node.raws.left = match[1];
            node.raws.right = match[3];
          }
        }
        createTokenizer() {
          this.tokenizer = tokenizer(this.input);
        }
        decl(tokens, customProperty) {
          let node = new Declaration2();
          this.init(node, tokens[0][2]);
          let last = tokens[tokens.length - 1];
          if (last[0] === ";") {
            this.semicolon = true;
            tokens.pop();
          }
          node.source.end = this.getPosition(
            last[3] || last[2] || findLastWithPosition(tokens)
          );
          node.source.end.offset++;
          while (tokens[0][0] !== "word") {
            if (tokens.length === 1) this.unknownWord(tokens);
            node.raws.before += tokens.shift()[1];
          }
          node.source.start = this.getPosition(tokens[0][2]);
          node.prop = "";
          while (tokens.length) {
            let type = tokens[0][0];
            if (type === ":" || type === "space" || type === "comment") {
              break;
            }
            node.prop += tokens.shift()[1];
          }
          node.raws.between = "";
          let token;
          while (tokens.length) {
            token = tokens.shift();
            if (token[0] === ":") {
              node.raws.between += token[1];
              break;
            } else {
              if (token[0] === "word" && /\w/.test(token[1])) {
                this.unknownWord([token]);
              }
              node.raws.between += token[1];
            }
          }
          if (node.prop[0] === "_" || node.prop[0] === "*") {
            node.raws.before += node.prop[0];
            node.prop = node.prop.slice(1);
          }
          let firstSpaces = [];
          let next;
          while (tokens.length) {
            next = tokens[0][0];
            if (next !== "space" && next !== "comment") break;
            firstSpaces.push(tokens.shift());
          }
          this.precheckMissedSemicolon(tokens);
          for (let i = tokens.length - 1; i >= 0; i--) {
            token = tokens[i];
            if (token[1].toLowerCase() === "!important") {
              node.important = true;
              let string = this.stringFrom(tokens, i);
              string = this.spacesFromEnd(tokens) + string;
              if (string !== " !important") node.raws.important = string;
              break;
            } else if (token[1].toLowerCase() === "important") {
              let cache = tokens.slice(0);
              let str = "";
              for (let j = i; j > 0; j--) {
                let type = cache[j][0];
                if (str.trim().startsWith("!") && type !== "space") {
                  break;
                }
                str = cache.pop()[1] + str;
              }
              if (str.trim().startsWith("!")) {
                node.important = true;
                node.raws.important = str;
                tokens = cache;
              }
            }
            if (token[0] !== "space" && token[0] !== "comment") {
              break;
            }
          }
          let hasWord = tokens.some((i) => i[0] !== "space" && i[0] !== "comment");
          if (hasWord) {
            node.raws.between += firstSpaces.map((i) => i[1]).join("");
            firstSpaces = [];
          }
          this.raw(node, "value", firstSpaces.concat(tokens), customProperty);
          if (node.value.includes(":") && !customProperty) {
            this.checkMissedSemicolon(tokens);
          }
        }
        doubleColon(token) {
          throw this.input.error(
            "Double colon",
            { offset: token[2] },
            { offset: token[2] + token[1].length }
          );
        }
        emptyRule(token) {
          let node = new Rule2();
          this.init(node, token[2]);
          node.selector = "";
          node.raws.between = "";
          this.current = node;
        }
        end(token) {
          if (this.current.nodes && this.current.nodes.length) {
            this.current.raws.semicolon = this.semicolon;
          }
          this.semicolon = false;
          this.current.raws.after = (this.current.raws.after || "") + this.spaces;
          this.spaces = "";
          if (this.current.parent) {
            this.current.source.end = this.getPosition(token[2]);
            this.current.source.end.offset++;
            this.current = this.current.parent;
          } else {
            this.unexpectedClose(token);
          }
        }
        endFile() {
          if (this.current.parent) this.unclosedBlock();
          if (this.current.nodes && this.current.nodes.length) {
            this.current.raws.semicolon = this.semicolon;
          }
          this.current.raws.after = (this.current.raws.after || "") + this.spaces;
          this.root.source.end = this.getPosition(this.tokenizer.position());
        }
        freeSemicolon(token) {
          this.spaces += token[1];
          if (this.current.nodes) {
            let prev = this.current.nodes[this.current.nodes.length - 1];
            if (prev && prev.type === "rule" && !prev.raws.ownSemicolon) {
              prev.raws.ownSemicolon = this.spaces;
              this.spaces = "";
              prev.source.end = this.getPosition(token[2]);
              prev.source.end.offset += prev.raws.ownSemicolon.length;
            }
          }
        }
        // Helpers
        getPosition(offset) {
          let pos = this.input.fromOffset(offset);
          return {
            column: pos.col,
            line: pos.line,
            offset
          };
        }
        init(node, offset) {
          this.current.push(node);
          node.source = {
            input: this.input,
            start: this.getPosition(offset)
          };
          node.raws.before = this.spaces;
          this.spaces = "";
          if (node.type !== "comment") this.semicolon = false;
        }
        other(start) {
          let end = false;
          let type = null;
          let colon = false;
          let bracket = null;
          let brackets = [];
          let customProperty = start[1].startsWith("--");
          let tokens = [];
          let token = start;
          while (token) {
            type = token[0];
            tokens.push(token);
            if (type === "(" || type === "[") {
              if (!bracket) bracket = token;
              brackets.push(type === "(" ? ")" : "]");
            } else if (customProperty && colon && type === "{") {
              if (!bracket) bracket = token;
              brackets.push("}");
            } else if (brackets.length === 0) {
              if (type === ";") {
                if (colon) {
                  this.decl(tokens, customProperty);
                  return;
                } else {
                  break;
                }
              } else if (type === "{") {
                this.rule(tokens);
                return;
              } else if (type === "}") {
                this.tokenizer.back(tokens.pop());
                end = true;
                break;
              } else if (type === ":") {
                colon = true;
              }
            } else if (type === brackets[brackets.length - 1]) {
              brackets.pop();
              if (brackets.length === 0) bracket = null;
            }
            token = this.tokenizer.nextToken();
          }
          if (this.tokenizer.endOfFile()) end = true;
          if (brackets.length > 0) this.unclosedBracket(bracket);
          if (end && colon) {
            if (!customProperty) {
              while (tokens.length) {
                token = tokens[tokens.length - 1][0];
                if (token !== "space" && token !== "comment") break;
                this.tokenizer.back(tokens.pop());
              }
            }
            this.decl(tokens, customProperty);
          } else {
            this.unknownWord(tokens);
          }
        }
        parse() {
          let token;
          while (!this.tokenizer.endOfFile()) {
            token = this.tokenizer.nextToken();
            switch (token[0]) {
              case "space":
                this.spaces += token[1];
                break;
              case ";":
                this.freeSemicolon(token);
                break;
              case "}":
                this.end(token);
                break;
              case "comment":
                this.comment(token);
                break;
              case "at-word":
                this.atrule(token);
                break;
              case "{":
                this.emptyRule(token);
                break;
              default:
                this.other(token);
                break;
            }
          }
          this.endFile();
        }
        precheckMissedSemicolon() {
        }
        raw(node, prop, tokens, customProperty) {
          let token, type;
          let length = tokens.length;
          let value = "";
          let clean = true;
          let next, prev;
          for (let i = 0; i < length; i += 1) {
            token = tokens[i];
            type = token[0];
            if (type === "space" && i === length - 1 && !customProperty) {
              clean = false;
            } else if (type === "comment") {
              prev = tokens[i - 1] ? tokens[i - 1][0] : "empty";
              next = tokens[i + 1] ? tokens[i + 1][0] : "empty";
              if (!SAFE_COMMENT_NEIGHBOR[prev] && !SAFE_COMMENT_NEIGHBOR[next]) {
                if (value.slice(-1) === ",") {
                  clean = false;
                } else {
                  value += token[1];
                }
              } else {
                clean = false;
              }
            } else {
              value += token[1];
            }
          }
          if (!clean) {
            let raw = tokens.reduce((all, i) => all + i[1], "");
            node.raws[prop] = { raw, value };
          }
          node[prop] = value;
        }
        rule(tokens) {
          tokens.pop();
          let node = new Rule2();
          this.init(node, tokens[0][2]);
          node.raws.between = this.spacesAndCommentsFromEnd(tokens);
          this.raw(node, "selector", tokens);
          this.current = node;
        }
        spacesAndCommentsFromEnd(tokens) {
          let lastTokenType;
          let spaces = "";
          while (tokens.length) {
            lastTokenType = tokens[tokens.length - 1][0];
            if (lastTokenType !== "space" && lastTokenType !== "comment") break;
            spaces = tokens.pop()[1] + spaces;
          }
          return spaces;
        }
        // Errors
        spacesAndCommentsFromStart(tokens) {
          let next;
          let spaces = "";
          while (tokens.length) {
            next = tokens[0][0];
            if (next !== "space" && next !== "comment") break;
            spaces += tokens.shift()[1];
          }
          return spaces;
        }
        spacesFromEnd(tokens) {
          let lastTokenType;
          let spaces = "";
          while (tokens.length) {
            lastTokenType = tokens[tokens.length - 1][0];
            if (lastTokenType !== "space") break;
            spaces = tokens.pop()[1] + spaces;
          }
          return spaces;
        }
        stringFrom(tokens, from) {
          let result = "";
          for (let i = from; i < tokens.length; i++) {
            result += tokens[i][1];
          }
          tokens.splice(from, tokens.length - from);
          return result;
        }
        unclosedBlock() {
          let pos = this.current.source.start;
          throw this.input.error("Unclosed block", pos.line, pos.column);
        }
        unclosedBracket(bracket) {
          throw this.input.error(
            "Unclosed bracket",
            { offset: bracket[2] },
            { offset: bracket[2] + 1 }
          );
        }
        unexpectedClose(token) {
          throw this.input.error(
            "Unexpected }",
            { offset: token[2] },
            { offset: token[2] + 1 }
          );
        }
        unknownWord(tokens) {
          throw this.input.error(
            "Unknown word " + tokens[0][1],
            { offset: tokens[0][2] },
            { offset: tokens[0][2] + tokens[0][1].length }
          );
        }
        unnamedAtrule(node, token) {
          throw this.input.error(
            "At-rule without name",
            { offset: token[2] },
            { offset: token[2] + token[1].length }
          );
        }
      };
      module.exports = Parser;
    }
  });

  // node_modules/postcss/lib/parse.js
  var require_parse = __commonJS({
    "node_modules/postcss/lib/parse.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var Input2 = require_input();
      var Parser = require_parser();
      function parse3(css, opts) {
        let input = new Input2(css, opts);
        let parser = new Parser(input);
        try {
          parser.parse();
        } catch (e) {
          if (true) {
            if (e.name === "CssSyntaxError" && opts && opts.from) {
              if (/\.scss$/i.test(opts.from)) {
                e.message += "\nYou tried to parse SCSS with the standard CSS parser; try again with the postcss-scss parser";
              } else if (/\.sass/i.test(opts.from)) {
                e.message += "\nYou tried to parse Sass with the standard CSS parser; try again with the postcss-sass parser";
              } else if (/\.less$/i.test(opts.from)) {
                e.message += "\nYou tried to parse Less with the standard CSS parser; try again with the postcss-less parser";
              }
            }
          }
          throw e;
        }
        return parser.root;
      }
      module.exports = parse3;
      parse3.default = parse3;
      Container2.registerParse(parse3);
    }
  });

  // node_modules/postcss/lib/warning.js
  var require_warning = __commonJS({
    "node_modules/postcss/lib/warning.js"(exports, module) {
      "use strict";
      var Warning2 = class {
        constructor(text, opts = {}) {
          this.type = "warning";
          this.text = text;
          if (opts.node && opts.node.source) {
            let range = opts.node.rangeBy(opts);
            this.line = range.start.line;
            this.column = range.start.column;
            this.endLine = range.end.line;
            this.endColumn = range.end.column;
          }
          for (let opt in opts) this[opt] = opts[opt];
        }
        toString() {
          if (this.node) {
            return this.node.error(this.text, {
              index: this.index,
              plugin: this.plugin,
              word: this.word
            }).message;
          }
          if (this.plugin) {
            return this.plugin + ": " + this.text;
          }
          return this.text;
        }
      };
      module.exports = Warning2;
      Warning2.default = Warning2;
    }
  });

  // node_modules/postcss/lib/result.js
  var require_result = __commonJS({
    "node_modules/postcss/lib/result.js"(exports, module) {
      "use strict";
      var Warning2 = require_warning();
      var Result2 = class {
        get content() {
          return this.css;
        }
        constructor(processor, root2, opts) {
          this.processor = processor;
          this.messages = [];
          this.root = root2;
          this.opts = opts;
          this.css = "";
          this.map = void 0;
        }
        toString() {
          return this.css;
        }
        warn(text, opts = {}) {
          if (!opts.plugin) {
            if (this.lastPlugin && this.lastPlugin.postcssPlugin) {
              opts.plugin = this.lastPlugin.postcssPlugin;
            }
          }
          let warning = new Warning2(text, opts);
          this.messages.push(warning);
          return warning;
        }
        warnings() {
          return this.messages.filter((i) => i.type === "warning");
        }
      };
      module.exports = Result2;
      Result2.default = Result2;
    }
  });

  // node_modules/postcss/lib/warn-once.js
  var require_warn_once = __commonJS({
    "node_modules/postcss/lib/warn-once.js"(exports, module) {
      "use strict";
      var printed = {};
      module.exports = function warnOnce(message) {
        if (printed[message]) return;
        printed[message] = true;
        if (typeof console !== "undefined" && console.warn) {
          console.warn(message);
        }
      };
    }
  });

  // node_modules/postcss/lib/lazy-result.js
  var require_lazy_result = __commonJS({
    "node_modules/postcss/lib/lazy-result.js"(exports, module) {
      "use strict";
      var Container2 = require_container();
      var Document2 = require_document();
      var MapGenerator = require_map_generator();
      var parse3 = require_parse();
      var Result2 = require_result();
      var Root2 = require_root();
      var stringify2 = require_stringify();
      var { isClean, my } = require_symbols();
      var warnOnce = require_warn_once();
      var TYPE_TO_CLASS_NAME = {
        atrule: "AtRule",
        comment: "Comment",
        decl: "Declaration",
        document: "Document",
        root: "Root",
        rule: "Rule"
      };
      var PLUGIN_PROPS = {
        AtRule: true,
        AtRuleExit: true,
        Comment: true,
        CommentExit: true,
        Declaration: true,
        DeclarationExit: true,
        Document: true,
        DocumentExit: true,
        Once: true,
        OnceExit: true,
        postcssPlugin: true,
        prepare: true,
        Root: true,
        RootExit: true,
        Rule: true,
        RuleExit: true
      };
      var NOT_VISITORS = {
        Once: true,
        postcssPlugin: true,
        prepare: true
      };
      var CHILDREN = 0;
      function isPromise(obj) {
        return typeof obj === "object" && typeof obj.then === "function";
      }
      function getEvents(node) {
        let key = false;
        let type = TYPE_TO_CLASS_NAME[node.type];
        if (node.type === "decl") {
          key = node.prop.toLowerCase();
        } else if (node.type === "atrule") {
          key = node.name.toLowerCase();
        }
        if (key && node.append) {
          return [
            type,
            type + "-" + key,
            CHILDREN,
            type + "Exit",
            type + "Exit-" + key
          ];
        } else if (key) {
          return [type, type + "-" + key, type + "Exit", type + "Exit-" + key];
        } else if (node.append) {
          return [type, CHILDREN, type + "Exit"];
        } else {
          return [type, type + "Exit"];
        }
      }
      function toStack(node) {
        let events;
        if (node.type === "document") {
          events = ["Document", CHILDREN, "DocumentExit"];
        } else if (node.type === "root") {
          events = ["Root", CHILDREN, "RootExit"];
        } else {
          events = getEvents(node);
        }
        return {
          eventIndex: 0,
          events,
          iterator: 0,
          node,
          visitorIndex: 0,
          visitors: []
        };
      }
      function cleanMarks(node) {
        node[isClean] = false;
        if (node.nodes) node.nodes.forEach((i) => cleanMarks(i));
        return node;
      }
      var postcss2 = {};
      var LazyResult = class _LazyResult {
        get content() {
          return this.stringify().content;
        }
        get css() {
          return this.stringify().css;
        }
        get map() {
          return this.stringify().map;
        }
        get messages() {
          return this.sync().messages;
        }
        get opts() {
          return this.result.opts;
        }
        get processor() {
          return this.result.processor;
        }
        get root() {
          return this.sync().root;
        }
        get [Symbol.toStringTag]() {
          return "LazyResult";
        }
        constructor(processor, css, opts) {
          this.stringified = false;
          this.processed = false;
          let root2;
          if (typeof css === "object" && css !== null && (css.type === "root" || css.type === "document")) {
            root2 = cleanMarks(css);
          } else if (css instanceof _LazyResult || css instanceof Result2) {
            root2 = cleanMarks(css.root);
            if (css.map) {
              if (typeof opts.map === "undefined") opts.map = {};
              if (!opts.map.inline) opts.map.inline = false;
              opts.map.prev = css.map;
            }
          } else {
            let parser = parse3;
            if (opts.syntax) parser = opts.syntax.parse;
            if (opts.parser) parser = opts.parser;
            if (parser.parse) parser = parser.parse;
            try {
              root2 = parser(css, opts);
            } catch (error) {
              this.processed = true;
              this.error = error;
            }
            if (root2 && !root2[my]) {
              Container2.rebuild(root2);
            }
          }
          this.result = new Result2(processor, root2, opts);
          this.helpers = { ...postcss2, postcss: postcss2, result: this.result };
          this.plugins = this.processor.plugins.map((plugin2) => {
            if (typeof plugin2 === "object" && plugin2.prepare) {
              return { ...plugin2, ...plugin2.prepare(this.result) };
            } else {
              return plugin2;
            }
          });
        }
        async() {
          if (this.error) return Promise.reject(this.error);
          if (this.processed) return Promise.resolve(this.result);
          if (!this.processing) {
            this.processing = this.runAsync();
          }
          return this.processing;
        }
        catch(onRejected) {
          return this.async().catch(onRejected);
        }
        finally(onFinally) {
          return this.async().then(onFinally, onFinally);
        }
        getAsyncError() {
          throw new Error("Use process(css).then(cb) to work with async plugins");
        }
        handleError(error, node) {
          let plugin2 = this.result.lastPlugin;
          try {
            if (node) node.addToError(error);
            this.error = error;
            if (error.name === "CssSyntaxError" && !error.plugin) {
              error.plugin = plugin2.postcssPlugin;
              error.setMessage();
            } else if (plugin2.postcssVersion) {
              if (true) {
                let pluginName = plugin2.postcssPlugin;
                let pluginVer = plugin2.postcssVersion;
                let runtimeVer = this.result.processor.version;
                let a = pluginVer.split(".");
                let b = runtimeVer.split(".");
                if (a[0] !== b[0] || parseInt(a[1]) > parseInt(b[1])) {
                  console.error(
                    "Unknown error from PostCSS plugin. Your current PostCSS version is " + runtimeVer + ", but " + pluginName + " uses " + pluginVer + ". Perhaps this is the source of the error below."
                  );
                }
              }
            }
          } catch (err) {
            if (console && console.error) console.error(err);
          }
          return error;
        }
        prepareVisitors() {
          this.listeners = {};
          let add = (plugin2, type, cb) => {
            if (!this.listeners[type]) this.listeners[type] = [];
            this.listeners[type].push([plugin2, cb]);
          };
          for (let plugin2 of this.plugins) {
            if (typeof plugin2 === "object") {
              for (let event in plugin2) {
                if (!PLUGIN_PROPS[event] && /^[A-Z]/.test(event)) {
                  throw new Error(
                    `Unknown event ${event} in ${plugin2.postcssPlugin}. Try to update PostCSS (${this.processor.version} now).`
                  );
                }
                if (!NOT_VISITORS[event]) {
                  if (typeof plugin2[event] === "object") {
                    for (let filter in plugin2[event]) {
                      if (filter === "*") {
                        add(plugin2, event, plugin2[event][filter]);
                      } else {
                        add(
                          plugin2,
                          event + "-" + filter.toLowerCase(),
                          plugin2[event][filter]
                        );
                      }
                    }
                  } else if (typeof plugin2[event] === "function") {
                    add(plugin2, event, plugin2[event]);
                  }
                }
              }
            }
          }
          this.hasListener = Object.keys(this.listeners).length > 0;
        }
        async runAsync() {
          this.plugin = 0;
          for (let i = 0; i < this.plugins.length; i++) {
            let plugin2 = this.plugins[i];
            let promise = this.runOnRoot(plugin2);
            if (isPromise(promise)) {
              try {
                await promise;
              } catch (error) {
                throw this.handleError(error);
              }
            }
          }
          this.prepareVisitors();
          if (this.hasListener) {
            let root2 = this.result.root;
            while (!root2[isClean]) {
              root2[isClean] = true;
              let stack = [toStack(root2)];
              while (stack.length > 0) {
                let promise = this.visitTick(stack);
                if (isPromise(promise)) {
                  try {
                    await promise;
                  } catch (e) {
                    let node = stack[stack.length - 1].node;
                    throw this.handleError(e, node);
                  }
                }
              }
            }
            if (this.listeners.OnceExit) {
              for (let [plugin2, visitor] of this.listeners.OnceExit) {
                this.result.lastPlugin = plugin2;
                try {
                  if (root2.type === "document") {
                    let roots = root2.nodes.map(
                      (subRoot) => visitor(subRoot, this.helpers)
                    );
                    await Promise.all(roots);
                  } else {
                    await visitor(root2, this.helpers);
                  }
                } catch (e) {
                  throw this.handleError(e);
                }
              }
            }
          }
          this.processed = true;
          return this.stringify();
        }
        runOnRoot(plugin2) {
          this.result.lastPlugin = plugin2;
          try {
            if (typeof plugin2 === "object" && plugin2.Once) {
              if (this.result.root.type === "document") {
                let roots = this.result.root.nodes.map(
                  (root2) => plugin2.Once(root2, this.helpers)
                );
                if (isPromise(roots[0])) {
                  return Promise.all(roots);
                }
                return roots;
              }
              return plugin2.Once(this.result.root, this.helpers);
            } else if (typeof plugin2 === "function") {
              return plugin2(this.result.root, this.result);
            }
          } catch (error) {
            throw this.handleError(error);
          }
        }
        stringify() {
          if (this.error) throw this.error;
          if (this.stringified) return this.result;
          this.stringified = true;
          this.sync();
          let opts = this.result.opts;
          let str = stringify2;
          if (opts.syntax) str = opts.syntax.stringify;
          if (opts.stringifier) str = opts.stringifier;
          if (str.stringify) str = str.stringify;
          let map = new MapGenerator(str, this.result.root, this.result.opts);
          let data = map.generate();
          this.result.css = data[0];
          this.result.map = data[1];
          return this.result;
        }
        sync() {
          if (this.error) throw this.error;
          if (this.processed) return this.result;
          this.processed = true;
          if (this.processing) {
            throw this.getAsyncError();
          }
          for (let plugin2 of this.plugins) {
            let promise = this.runOnRoot(plugin2);
            if (isPromise(promise)) {
              throw this.getAsyncError();
            }
          }
          this.prepareVisitors();
          if (this.hasListener) {
            let root2 = this.result.root;
            while (!root2[isClean]) {
              root2[isClean] = true;
              this.walkSync(root2);
            }
            if (this.listeners.OnceExit) {
              if (root2.type === "document") {
                for (let subRoot of root2.nodes) {
                  this.visitSync(this.listeners.OnceExit, subRoot);
                }
              } else {
                this.visitSync(this.listeners.OnceExit, root2);
              }
            }
          }
          return this.result;
        }
        then(onFulfilled, onRejected) {
          if (true) {
            if (!("from" in this.opts)) {
              warnOnce(
                "Without `from` option PostCSS could generate wrong source map and will not find Browserslist config. Set it to CSS file path or to `undefined` to prevent this warning."
              );
            }
          }
          return this.async().then(onFulfilled, onRejected);
        }
        toString() {
          return this.css;
        }
        visitSync(visitors, node) {
          for (let [plugin2, visitor] of visitors) {
            this.result.lastPlugin = plugin2;
            let promise;
            try {
              promise = visitor(node, this.helpers);
            } catch (e) {
              throw this.handleError(e, node.proxyOf);
            }
            if (node.type !== "root" && node.type !== "document" && !node.parent) {
              return true;
            }
            if (isPromise(promise)) {
              throw this.getAsyncError();
            }
          }
        }
        visitTick(stack) {
          let visit = stack[stack.length - 1];
          let { node, visitors } = visit;
          if (node.type !== "root" && node.type !== "document" && !node.parent) {
            stack.pop();
            return;
          }
          if (visitors.length > 0 && visit.visitorIndex < visitors.length) {
            let [plugin2, visitor] = visitors[visit.visitorIndex];
            visit.visitorIndex += 1;
            if (visit.visitorIndex === visitors.length) {
              visit.visitors = [];
              visit.visitorIndex = 0;
            }
            this.result.lastPlugin = plugin2;
            try {
              return visitor(node.toProxy(), this.helpers);
            } catch (e) {
              throw this.handleError(e, node);
            }
          }
          if (visit.iterator !== 0) {
            let iterator = visit.iterator;
            let child;
            while (child = node.nodes[node.indexes[iterator]]) {
              node.indexes[iterator] += 1;
              if (!child[isClean]) {
                child[isClean] = true;
                stack.push(toStack(child));
                return;
              }
            }
            visit.iterator = 0;
            delete node.indexes[iterator];
          }
          let events = visit.events;
          while (visit.eventIndex < events.length) {
            let event = events[visit.eventIndex];
            visit.eventIndex += 1;
            if (event === CHILDREN) {
              if (node.nodes && node.nodes.length) {
                node[isClean] = true;
                visit.iterator = node.getIterator();
              }
              return;
            } else if (this.listeners[event]) {
              visit.visitors = this.listeners[event];
              return;
            }
          }
          stack.pop();
        }
        walkSync(node) {
          node[isClean] = true;
          let events = getEvents(node);
          for (let event of events) {
            if (event === CHILDREN) {
              if (node.nodes) {
                node.each((child) => {
                  if (!child[isClean]) this.walkSync(child);
                });
              }
            } else {
              let visitors = this.listeners[event];
              if (visitors) {
                if (this.visitSync(visitors, node.toProxy())) return;
              }
            }
          }
        }
        warnings() {
          return this.sync().warnings();
        }
      };
      LazyResult.registerPostcss = (dependant) => {
        postcss2 = dependant;
      };
      module.exports = LazyResult;
      LazyResult.default = LazyResult;
      Root2.registerLazyResult(LazyResult);
      Document2.registerLazyResult(LazyResult);
    }
  });

  // node_modules/postcss/lib/no-work-result.js
  var require_no_work_result = __commonJS({
    "node_modules/postcss/lib/no-work-result.js"(exports, module) {
      "use strict";
      var MapGenerator = require_map_generator();
      var parse3 = require_parse();
      var Result2 = require_result();
      var stringify2 = require_stringify();
      var warnOnce = require_warn_once();
      var NoWorkResult = class {
        get content() {
          return this.result.css;
        }
        get css() {
          return this.result.css;
        }
        get map() {
          return this.result.map;
        }
        get messages() {
          return [];
        }
        get opts() {
          return this.result.opts;
        }
        get processor() {
          return this.result.processor;
        }
        get root() {
          if (this._root) {
            return this._root;
          }
          let root2;
          let parser = parse3;
          try {
            root2 = parser(this._css, this._opts);
          } catch (error) {
            this.error = error;
          }
          if (this.error) {
            throw this.error;
          } else {
            this._root = root2;
            return root2;
          }
        }
        get [Symbol.toStringTag]() {
          return "NoWorkResult";
        }
        constructor(processor, css, opts) {
          css = css.toString();
          this.stringified = false;
          this._processor = processor;
          this._css = css;
          this._opts = opts;
          this._map = void 0;
          let root2;
          let str = stringify2;
          this.result = new Result2(this._processor, root2, this._opts);
          this.result.css = css;
          let self = this;
          Object.defineProperty(this.result, "root", {
            get() {
              return self.root;
            }
          });
          let map = new MapGenerator(str, root2, this._opts, css);
          if (map.isMap()) {
            let [generatedCSS, generatedMap] = map.generate();
            if (generatedCSS) {
              this.result.css = generatedCSS;
            }
            if (generatedMap) {
              this.result.map = generatedMap;
            }
          } else {
            map.clearAnnotation();
            this.result.css = map.css;
          }
        }
        async() {
          if (this.error) return Promise.reject(this.error);
          return Promise.resolve(this.result);
        }
        catch(onRejected) {
          return this.async().catch(onRejected);
        }
        finally(onFinally) {
          return this.async().then(onFinally, onFinally);
        }
        sync() {
          if (this.error) throw this.error;
          return this.result;
        }
        then(onFulfilled, onRejected) {
          if (true) {
            if (!("from" in this._opts)) {
              warnOnce(
                "Without `from` option PostCSS could generate wrong source map and will not find Browserslist config. Set it to CSS file path or to `undefined` to prevent this warning."
              );
            }
          }
          return this.async().then(onFulfilled, onRejected);
        }
        toString() {
          return this._css;
        }
        warnings() {
          return [];
        }
      };
      module.exports = NoWorkResult;
      NoWorkResult.default = NoWorkResult;
    }
  });

  // node_modules/postcss/lib/processor.js
  var require_processor = __commonJS({
    "node_modules/postcss/lib/processor.js"(exports, module) {
      "use strict";
      var Document2 = require_document();
      var LazyResult = require_lazy_result();
      var NoWorkResult = require_no_work_result();
      var Root2 = require_root();
      var Processor2 = class {
        constructor(plugins = []) {
          this.version = "8.5.6";
          this.plugins = this.normalize(plugins);
        }
        normalize(plugins) {
          let normalized = [];
          for (let i of plugins) {
            if (i.postcss === true) {
              i = i();
            } else if (i.postcss) {
              i = i.postcss;
            }
            if (typeof i === "object" && Array.isArray(i.plugins)) {
              normalized = normalized.concat(i.plugins);
            } else if (typeof i === "object" && i.postcssPlugin) {
              normalized.push(i);
            } else if (typeof i === "function") {
              normalized.push(i);
            } else if (typeof i === "object" && (i.parse || i.stringify)) {
              if (true) {
                throw new Error(
                  "PostCSS syntaxes cannot be used as plugins. Instead, please use one of the syntax/parser/stringifier options as outlined in your PostCSS runner documentation."
                );
              }
            } else {
              throw new Error(i + " is not a PostCSS plugin");
            }
          }
          return normalized;
        }
        process(css, opts = {}) {
          if (!this.plugins.length && !opts.parser && !opts.stringifier && !opts.syntax) {
            return new NoWorkResult(this, css, opts);
          } else {
            return new LazyResult(this, css, opts);
          }
        }
        use(plugin2) {
          this.plugins = this.plugins.concat(this.normalize([plugin2]));
          return this;
        }
      };
      module.exports = Processor2;
      Processor2.default = Processor2;
      Root2.registerProcessor(Processor2);
      Document2.registerProcessor(Processor2);
    }
  });

  // node_modules/postcss/lib/postcss.js
  var require_postcss = __commonJS({
    "node_modules/postcss/lib/postcss.js"(exports, module) {
      "use strict";
      var AtRule2 = require_at_rule();
      var Comment2 = require_comment();
      var Container2 = require_container();
      var CssSyntaxError2 = require_css_syntax_error();
      var Declaration2 = require_declaration();
      var Document2 = require_document();
      var fromJSON2 = require_fromJSON();
      var Input2 = require_input();
      var LazyResult = require_lazy_result();
      var list2 = require_list();
      var Node3 = require_node();
      var parse3 = require_parse();
      var Processor2 = require_processor();
      var Result2 = require_result();
      var Root2 = require_root();
      var Rule2 = require_rule();
      var stringify2 = require_stringify();
      var Warning2 = require_warning();
      function postcss2(...plugins) {
        if (plugins.length === 1 && Array.isArray(plugins[0])) {
          plugins = plugins[0];
        }
        return new Processor2(plugins);
      }
      postcss2.plugin = function plugin2(name, initializer) {
        let warningPrinted = false;
        function creator(...args) {
          if (console && console.warn && !warningPrinted) {
            warningPrinted = true;
            console.warn(
              name + ": postcss.plugin was deprecated. Migration guide:\nhttps://evilmartians.com/chronicles/postcss-8-plugin-migration"
            );
            if (process.env.LANG && process.env.LANG.startsWith("cn")) {
              console.warn(
                name + ": \u91CC\u9762 postcss.plugin \u88AB\u5F03\u7528. \u8FC1\u79FB\u6307\u5357:\nhttps://www.w3ctech.com/topic/2226"
              );
            }
          }
          let transformer = initializer(...args);
          transformer.postcssPlugin = name;
          transformer.postcssVersion = new Processor2().version;
          return transformer;
        }
        let cache;
        Object.defineProperty(creator, "postcss", {
          get() {
            if (!cache) cache = creator();
            return cache;
          }
        });
        creator.process = function(css, processOpts, pluginOpts) {
          return postcss2([creator(pluginOpts)]).process(css, processOpts);
        };
        return creator;
      };
      postcss2.stringify = stringify2;
      postcss2.parse = parse3;
      postcss2.fromJSON = fromJSON2;
      postcss2.list = list2;
      postcss2.comment = (defaults2) => new Comment2(defaults2);
      postcss2.atRule = (defaults2) => new AtRule2(defaults2);
      postcss2.decl = (defaults2) => new Declaration2(defaults2);
      postcss2.rule = (defaults2) => new Rule2(defaults2);
      postcss2.root = (defaults2) => new Root2(defaults2);
      postcss2.document = (defaults2) => new Document2(defaults2);
      postcss2.CssSyntaxError = CssSyntaxError2;
      postcss2.Declaration = Declaration2;
      postcss2.Container = Container2;
      postcss2.Processor = Processor2;
      postcss2.Document = Document2;
      postcss2.Comment = Comment2;
      postcss2.Warning = Warning2;
      postcss2.AtRule = AtRule2;
      postcss2.Result = Result2;
      postcss2.Input = Input2;
      postcss2.Rule = Rule2;
      postcss2.Root = Root2;
      postcss2.Node = Node3;
      LazyResult.registerPostcss(postcss2);
      module.exports = postcss2;
      postcss2.default = postcss2;
    }
  });

  // node_modules/postcss-value-parser/lib/parse.js
  var require_parse2 = __commonJS({
    "node_modules/postcss-value-parser/lib/parse.js"(exports, module) {
      var openParentheses = "(".charCodeAt(0);
      var closeParentheses = ")".charCodeAt(0);
      var singleQuote = "'".charCodeAt(0);
      var doubleQuote = '"'.charCodeAt(0);
      var backslash = "\\".charCodeAt(0);
      var slash = "/".charCodeAt(0);
      var comma = ",".charCodeAt(0);
      var colon = ":".charCodeAt(0);
      var star = "*".charCodeAt(0);
      var uLower = "u".charCodeAt(0);
      var uUpper = "U".charCodeAt(0);
      var plus = "+".charCodeAt(0);
      var isUnicodeRange = /^[a-f0-9?-]+$/i;
      module.exports = function(input) {
        var tokens = [];
        var value = input;
        var next, quote, prev, token, escape, escapePos, whitespacePos, parenthesesOpenPos;
        var pos = 0;
        var code = value.charCodeAt(pos);
        var max = value.length;
        var stack = [{ nodes: tokens }];
        var balanced = 0;
        var parent;
        var name = "";
        var before = "";
        var after = "";
        while (pos < max) {
          if (code <= 32) {
            next = pos;
            do {
              next += 1;
              code = value.charCodeAt(next);
            } while (code <= 32);
            token = value.slice(pos, next);
            prev = tokens[tokens.length - 1];
            if (code === closeParentheses && balanced) {
              after = token;
            } else if (prev && prev.type === "div") {
              prev.after = token;
              prev.sourceEndIndex += token.length;
            } else if (code === comma || code === colon || code === slash && value.charCodeAt(next + 1) !== star && (!parent || parent && parent.type === "function" && parent.value !== "calc")) {
              before = token;
            } else {
              tokens.push({
                type: "space",
                sourceIndex: pos,
                sourceEndIndex: next,
                value: token
              });
            }
            pos = next;
          } else if (code === singleQuote || code === doubleQuote) {
            next = pos;
            quote = code === singleQuote ? "'" : '"';
            token = {
              type: "string",
              sourceIndex: pos,
              quote
            };
            do {
              escape = false;
              next = value.indexOf(quote, next + 1);
              if (~next) {
                escapePos = next;
                while (value.charCodeAt(escapePos - 1) === backslash) {
                  escapePos -= 1;
                  escape = !escape;
                }
              } else {
                value += quote;
                next = value.length - 1;
                token.unclosed = true;
              }
            } while (escape);
            token.value = value.slice(pos + 1, next);
            token.sourceEndIndex = token.unclosed ? next : next + 1;
            tokens.push(token);
            pos = next + 1;
            code = value.charCodeAt(pos);
          } else if (code === slash && value.charCodeAt(pos + 1) === star) {
            next = value.indexOf("*/", pos);
            token = {
              type: "comment",
              sourceIndex: pos,
              sourceEndIndex: next + 2
            };
            if (next === -1) {
              token.unclosed = true;
              next = value.length;
              token.sourceEndIndex = next;
            }
            token.value = value.slice(pos + 2, next);
            tokens.push(token);
            pos = next + 2;
            code = value.charCodeAt(pos);
          } else if ((code === slash || code === star) && parent && parent.type === "function" && parent.value === "calc") {
            token = value[pos];
            tokens.push({
              type: "word",
              sourceIndex: pos - before.length,
              sourceEndIndex: pos + token.length,
              value: token
            });
            pos += 1;
            code = value.charCodeAt(pos);
          } else if (code === slash || code === comma || code === colon) {
            token = value[pos];
            tokens.push({
              type: "div",
              sourceIndex: pos - before.length,
              sourceEndIndex: pos + token.length,
              value: token,
              before,
              after: ""
            });
            before = "";
            pos += 1;
            code = value.charCodeAt(pos);
          } else if (openParentheses === code) {
            next = pos;
            do {
              next += 1;
              code = value.charCodeAt(next);
            } while (code <= 32);
            parenthesesOpenPos = pos;
            token = {
              type: "function",
              sourceIndex: pos - name.length,
              value: name,
              before: value.slice(parenthesesOpenPos + 1, next)
            };
            pos = next;
            if (name === "url" && code !== singleQuote && code !== doubleQuote) {
              next -= 1;
              do {
                escape = false;
                next = value.indexOf(")", next + 1);
                if (~next) {
                  escapePos = next;
                  while (value.charCodeAt(escapePos - 1) === backslash) {
                    escapePos -= 1;
                    escape = !escape;
                  }
                } else {
                  value += ")";
                  next = value.length - 1;
                  token.unclosed = true;
                }
              } while (escape);
              whitespacePos = next;
              do {
                whitespacePos -= 1;
                code = value.charCodeAt(whitespacePos);
              } while (code <= 32);
              if (parenthesesOpenPos < whitespacePos) {
                if (pos !== whitespacePos + 1) {
                  token.nodes = [
                    {
                      type: "word",
                      sourceIndex: pos,
                      sourceEndIndex: whitespacePos + 1,
                      value: value.slice(pos, whitespacePos + 1)
                    }
                  ];
                } else {
                  token.nodes = [];
                }
                if (token.unclosed && whitespacePos + 1 !== next) {
                  token.after = "";
                  token.nodes.push({
                    type: "space",
                    sourceIndex: whitespacePos + 1,
                    sourceEndIndex: next,
                    value: value.slice(whitespacePos + 1, next)
                  });
                } else {
                  token.after = value.slice(whitespacePos + 1, next);
                  token.sourceEndIndex = next;
                }
              } else {
                token.after = "";
                token.nodes = [];
              }
              pos = next + 1;
              token.sourceEndIndex = token.unclosed ? next : pos;
              code = value.charCodeAt(pos);
              tokens.push(token);
            } else {
              balanced += 1;
              token.after = "";
              token.sourceEndIndex = pos + 1;
              tokens.push(token);
              stack.push(token);
              tokens = token.nodes = [];
              parent = token;
            }
            name = "";
          } else if (closeParentheses === code && balanced) {
            pos += 1;
            code = value.charCodeAt(pos);
            parent.after = after;
            parent.sourceEndIndex += after.length;
            after = "";
            balanced -= 1;
            stack[stack.length - 1].sourceEndIndex = pos;
            stack.pop();
            parent = stack[balanced];
            tokens = parent.nodes;
          } else {
            next = pos;
            do {
              if (code === backslash) {
                next += 1;
              }
              next += 1;
              code = value.charCodeAt(next);
            } while (next < max && !(code <= 32 || code === singleQuote || code === doubleQuote || code === comma || code === colon || code === slash || code === openParentheses || code === star && parent && parent.type === "function" && parent.value === "calc" || code === slash && parent.type === "function" && parent.value === "calc" || code === closeParentheses && balanced));
            token = value.slice(pos, next);
            if (openParentheses === code) {
              name = token;
            } else if ((uLower === token.charCodeAt(0) || uUpper === token.charCodeAt(0)) && plus === token.charCodeAt(1) && isUnicodeRange.test(token.slice(2))) {
              tokens.push({
                type: "unicode-range",
                sourceIndex: pos,
                sourceEndIndex: next,
                value: token
              });
            } else {
              tokens.push({
                type: "word",
                sourceIndex: pos,
                sourceEndIndex: next,
                value: token
              });
            }
            pos = next;
          }
        }
        for (pos = stack.length - 1; pos; pos -= 1) {
          stack[pos].unclosed = true;
          stack[pos].sourceEndIndex = value.length;
        }
        return stack[0].nodes;
      };
    }
  });

  // node_modules/postcss-value-parser/lib/walk.js
  var require_walk = __commonJS({
    "node_modules/postcss-value-parser/lib/walk.js"(exports, module) {
      module.exports = function walk(nodes, cb, bubble) {
        var i, max, node, result;
        for (i = 0, max = nodes.length; i < max; i += 1) {
          node = nodes[i];
          if (!bubble) {
            result = cb(node, i, nodes);
          }
          if (result !== false && node.type === "function" && Array.isArray(node.nodes)) {
            walk(node.nodes, cb, bubble);
          }
          if (bubble) {
            cb(node, i, nodes);
          }
        }
      };
    }
  });

  // node_modules/postcss-value-parser/lib/stringify.js
  var require_stringify2 = __commonJS({
    "node_modules/postcss-value-parser/lib/stringify.js"(exports, module) {
      function stringifyNode(node, custom) {
        var type = node.type;
        var value = node.value;
        var buf;
        var customResult;
        if (custom && (customResult = custom(node)) !== void 0) {
          return customResult;
        } else if (type === "word" || type === "space") {
          return value;
        } else if (type === "string") {
          buf = node.quote || "";
          return buf + value + (node.unclosed ? "" : buf);
        } else if (type === "comment") {
          return "/*" + value + (node.unclosed ? "" : "*/");
        } else if (type === "div") {
          return (node.before || "") + value + (node.after || "");
        } else if (Array.isArray(node.nodes)) {
          buf = stringify2(node.nodes, custom);
          if (type !== "function") {
            return buf;
          }
          return value + "(" + (node.before || "") + buf + (node.after || "") + (node.unclosed ? "" : ")");
        }
        return value;
      }
      function stringify2(nodes, custom) {
        var result, i;
        if (Array.isArray(nodes)) {
          result = "";
          for (i = nodes.length - 1; ~i; i -= 1) {
            result = stringifyNode(nodes[i], custom) + result;
          }
          return result;
        }
        return stringifyNode(nodes, custom);
      }
      module.exports = stringify2;
    }
  });

  // node_modules/postcss-value-parser/lib/unit.js
  var require_unit = __commonJS({
    "node_modules/postcss-value-parser/lib/unit.js"(exports, module) {
      var minus = "-".charCodeAt(0);
      var plus = "+".charCodeAt(0);
      var dot = ".".charCodeAt(0);
      var exp = "e".charCodeAt(0);
      var EXP = "E".charCodeAt(0);
      function likeNumber(value) {
        var code = value.charCodeAt(0);
        var nextCode;
        if (code === plus || code === minus) {
          nextCode = value.charCodeAt(1);
          if (nextCode >= 48 && nextCode <= 57) {
            return true;
          }
          var nextNextCode = value.charCodeAt(2);
          if (nextCode === dot && nextNextCode >= 48 && nextNextCode <= 57) {
            return true;
          }
          return false;
        }
        if (code === dot) {
          nextCode = value.charCodeAt(1);
          if (nextCode >= 48 && nextCode <= 57) {
            return true;
          }
          return false;
        }
        if (code >= 48 && code <= 57) {
          return true;
        }
        return false;
      }
      module.exports = function(value) {
        var pos = 0;
        var length = value.length;
        var code;
        var nextCode;
        var nextNextCode;
        if (length === 0 || !likeNumber(value)) {
          return false;
        }
        code = value.charCodeAt(pos);
        if (code === plus || code === minus) {
          pos++;
        }
        while (pos < length) {
          code = value.charCodeAt(pos);
          if (code < 48 || code > 57) {
            break;
          }
          pos += 1;
        }
        code = value.charCodeAt(pos);
        nextCode = value.charCodeAt(pos + 1);
        if (code === dot && nextCode >= 48 && nextCode <= 57) {
          pos += 2;
          while (pos < length) {
            code = value.charCodeAt(pos);
            if (code < 48 || code > 57) {
              break;
            }
            pos += 1;
          }
        }
        code = value.charCodeAt(pos);
        nextCode = value.charCodeAt(pos + 1);
        nextNextCode = value.charCodeAt(pos + 2);
        if ((code === exp || code === EXP) && (nextCode >= 48 && nextCode <= 57 || (nextCode === plus || nextCode === minus) && nextNextCode >= 48 && nextNextCode <= 57)) {
          pos += nextCode === plus || nextCode === minus ? 3 : 2;
          while (pos < length) {
            code = value.charCodeAt(pos);
            if (code < 48 || code > 57) {
              break;
            }
            pos += 1;
          }
        }
        return {
          number: value.slice(0, pos),
          unit: value.slice(pos)
        };
      };
    }
  });

  // node_modules/postcss-value-parser/lib/index.js
  var require_lib = __commonJS({
    "node_modules/postcss-value-parser/lib/index.js"(exports, module) {
      var parse3 = require_parse2();
      var walk = require_walk();
      var stringify2 = require_stringify2();
      function ValueParser(value) {
        if (this instanceof ValueParser) {
          this.nodes = parse3(value);
          return this;
        }
        return new ValueParser(value);
      }
      ValueParser.prototype.toString = function() {
        return Array.isArray(this.nodes) ? stringify2(this.nodes) : "";
      };
      ValueParser.prototype.walk = function(cb, bubble) {
        walk(this.nodes, cb, bubble);
        return this;
      };
      ValueParser.unit = require_unit();
      ValueParser.walk = walk;
      ValueParser.stringify = stringify2;
      module.exports = ValueParser;
    }
  });

  // node_modules/gradient-parser/build/node.js
  var require_node2 = __commonJS({
    "node_modules/gradient-parser/build/node.js"(exports) {
      var GradientParser = GradientParser || {};
      GradientParser.stringify = /* @__PURE__ */ (function() {
        var visitor = {
          "visit_linear-gradient": function(node) {
            return visitor.visit_gradient(node);
          },
          "visit_repeating-linear-gradient": function(node) {
            return visitor.visit_gradient(node);
          },
          "visit_radial-gradient": function(node) {
            return visitor.visit_gradient(node);
          },
          "visit_repeating-radial-gradient": function(node) {
            return visitor.visit_gradient(node);
          },
          "visit_gradient": function(node) {
            var orientation = visitor.visit(node.orientation);
            if (orientation) {
              orientation += ", ";
            }
            return node.type + "(" + orientation + visitor.visit(node.colorStops) + ")";
          },
          "visit_shape": function(node) {
            var result = node.value, at = visitor.visit(node.at), style = visitor.visit(node.style);
            if (style) {
              result += " " + style;
            }
            if (at) {
              result += " at " + at;
            }
            return result;
          },
          "visit_default-radial": function(node) {
            var result = "", at = visitor.visit(node.at);
            if (at) {
              result += at;
            }
            return result;
          },
          "visit_extent-keyword": function(node) {
            var result = node.value, at = visitor.visit(node.at);
            if (at) {
              result += " at " + at;
            }
            return result;
          },
          "visit_position-keyword": function(node) {
            return node.value;
          },
          "visit_position": function(node) {
            return visitor.visit(node.value.x) + " " + visitor.visit(node.value.y);
          },
          "visit_%": function(node) {
            return node.value + "%";
          },
          "visit_em": function(node) {
            return node.value + "em";
          },
          "visit_px": function(node) {
            return node.value + "px";
          },
          "visit_calc": function(node) {
            return "calc(" + node.value + ")";
          },
          "visit_literal": function(node) {
            return visitor.visit_color(node.value, node);
          },
          "visit_hex": function(node) {
            return visitor.visit_color("#" + node.value, node);
          },
          "visit_rgb": function(node) {
            return visitor.visit_color("rgb(" + node.value.join(", ") + ")", node);
          },
          "visit_rgba": function(node) {
            return visitor.visit_color("rgba(" + node.value.join(", ") + ")", node);
          },
          "visit_hsl": function(node) {
            return visitor.visit_color("hsl(" + node.value[0] + ", " + node.value[1] + "%, " + node.value[2] + "%)", node);
          },
          "visit_hsla": function(node) {
            return visitor.visit_color("hsla(" + node.value[0] + ", " + node.value[1] + "%, " + node.value[2] + "%, " + node.value[3] + ")", node);
          },
          "visit_var": function(node) {
            return visitor.visit_color("var(" + node.value + ")", node);
          },
          "visit_color": function(resultColor, node) {
            var result = resultColor, length = visitor.visit(node.length);
            if (length) {
              result += " " + length;
            }
            return result;
          },
          "visit_angular": function(node) {
            return node.value + "deg";
          },
          "visit_directional": function(node) {
            return "to " + node.value;
          },
          "visit_array": function(elements) {
            var result = "", size = elements.length;
            elements.forEach(function(element, i) {
              result += visitor.visit(element);
              if (i < size - 1) {
                result += ", ";
              }
            });
            return result;
          },
          "visit_object": function(obj) {
            if (obj.width && obj.height) {
              return visitor.visit(obj.width) + " " + visitor.visit(obj.height);
            }
            return "";
          },
          "visit": function(element) {
            if (!element) {
              return "";
            }
            var result = "";
            if (element instanceof Array) {
              return visitor.visit_array(element);
            } else if (typeof element === "object" && !element.type) {
              return visitor.visit_object(element);
            } else if (element.type) {
              var nodeVisitor = visitor["visit_" + element.type];
              if (nodeVisitor) {
                return nodeVisitor(element);
              } else {
                throw Error("Missing visitor visit_" + element.type);
              }
            } else {
              throw Error("Invalid node.");
            }
          }
        };
        return function(root2) {
          return visitor.visit(root2);
        };
      })();
      var GradientParser = GradientParser || {};
      GradientParser.parse = /* @__PURE__ */ (function() {
        var tokens = {
          linearGradient: /^(\-(webkit|o|ms|moz)\-)?(linear\-gradient)/i,
          repeatingLinearGradient: /^(\-(webkit|o|ms|moz)\-)?(repeating\-linear\-gradient)/i,
          radialGradient: /^(\-(webkit|o|ms|moz)\-)?(radial\-gradient)/i,
          repeatingRadialGradient: /^(\-(webkit|o|ms|moz)\-)?(repeating\-radial\-gradient)/i,
          sideOrCorner: /^to (left (top|bottom)|right (top|bottom)|top (left|right)|bottom (left|right)|left|right|top|bottom)/i,
          extentKeywords: /^(closest\-side|closest\-corner|farthest\-side|farthest\-corner|contain|cover)/,
          positionKeywords: /^(left|center|right|top|bottom)/i,
          pixelValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))px/,
          percentageValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))\%/,
          emValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))em/,
          angleValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))deg/,
          radianValue: /^(-?(([0-9]*\.[0-9]+)|([0-9]+\.?)))rad/,
          startCall: /^\(/,
          endCall: /^\)/,
          comma: /^,/,
          hexColor: /^\#([0-9a-fA-F]+)/,
          literalColor: /^([a-zA-Z]+)/,
          rgbColor: /^rgb/i,
          rgbaColor: /^rgba/i,
          varColor: /^var/i,
          calcValue: /^calc/i,
          variableName: /^(--[a-zA-Z0-9-,\s\#]+)/,
          number: /^(([0-9]*\.[0-9]+)|([0-9]+\.?))/,
          hslColor: /^hsl/i,
          hslaColor: /^hsla/i
        };
        var input = "";
        function error(msg) {
          var err = new Error(input + ": " + msg);
          err.source = input;
          throw err;
        }
        function getAST() {
          var ast = matchListDefinitions();
          if (input.length > 0) {
            error("Invalid input not EOF");
          }
          return ast;
        }
        function matchListDefinitions() {
          return matchListing(matchDefinition);
        }
        function matchDefinition() {
          return matchGradient(
            "linear-gradient",
            tokens.linearGradient,
            matchLinearOrientation
          ) || matchGradient(
            "repeating-linear-gradient",
            tokens.repeatingLinearGradient,
            matchLinearOrientation
          ) || matchGradient(
            "radial-gradient",
            tokens.radialGradient,
            matchListRadialOrientations
          ) || matchGradient(
            "repeating-radial-gradient",
            tokens.repeatingRadialGradient,
            matchListRadialOrientations
          );
        }
        function matchGradient(gradientType, pattern, orientationMatcher) {
          return matchCall(pattern, function(captures) {
            var orientation = orientationMatcher();
            if (orientation) {
              if (!scan(tokens.comma)) {
                error("Missing comma before color stops");
              }
            }
            return {
              type: gradientType,
              orientation,
              colorStops: matchListing(matchColorStop)
            };
          });
        }
        function matchCall(pattern, callback) {
          var captures = scan(pattern);
          if (captures) {
            if (!scan(tokens.startCall)) {
              error("Missing (");
            }
            var result = callback(captures);
            if (!scan(tokens.endCall)) {
              error("Missing )");
            }
            return result;
          }
        }
        function matchLinearOrientation() {
          var sideOrCorner = matchSideOrCorner();
          if (sideOrCorner) {
            return sideOrCorner;
          }
          var legacyDirection = match("position-keyword", tokens.positionKeywords, 1);
          if (legacyDirection) {
            return {
              type: "directional",
              value: legacyDirection.value
            };
          }
          return matchAngle();
        }
        function matchSideOrCorner() {
          return match("directional", tokens.sideOrCorner, 1);
        }
        function matchAngle() {
          return match("angular", tokens.angleValue, 1) || match("angular", tokens.radianValue, 1);
        }
        function matchListRadialOrientations() {
          var radialOrientations, radialOrientation = matchRadialOrientation(), lookaheadCache;
          if (radialOrientation) {
            radialOrientations = [];
            radialOrientations.push(radialOrientation);
            lookaheadCache = input;
            if (scan(tokens.comma)) {
              radialOrientation = matchRadialOrientation();
              if (radialOrientation) {
                radialOrientations.push(radialOrientation);
              } else {
                input = lookaheadCache;
              }
            }
          }
          return radialOrientations;
        }
        function matchRadialOrientation() {
          var radialType = matchCircle() || matchEllipse();
          if (radialType) {
            radialType.at = matchAtPosition();
          } else {
            var extent = matchExtentKeyword();
            if (extent) {
              radialType = extent;
              var positionAt = matchAtPosition();
              if (positionAt) {
                radialType.at = positionAt;
              }
            } else {
              var atPosition = matchAtPosition();
              if (atPosition) {
                radialType = {
                  type: "default-radial",
                  at: atPosition
                };
              } else {
                var defaultPosition = matchPositioning();
                if (defaultPosition) {
                  radialType = {
                    type: "default-radial",
                    at: defaultPosition
                  };
                }
              }
            }
          }
          return radialType;
        }
        function matchCircle() {
          var circle = match("shape", /^(circle)/i, 0);
          if (circle) {
            circle.style = matchLength() || matchExtentKeyword();
          }
          return circle;
        }
        function matchEllipse() {
          var ellipse = match("shape", /^(ellipse)/i, 0);
          if (ellipse) {
            ellipse.style = matchPositioning() || matchDistance() || matchExtentKeyword();
          }
          return ellipse;
        }
        function matchExtentKeyword() {
          return match("extent-keyword", tokens.extentKeywords, 1);
        }
        function matchAtPosition() {
          if (match("position", /^at/, 0)) {
            var positioning = matchPositioning();
            if (!positioning) {
              error("Missing positioning value");
            }
            return positioning;
          }
        }
        function matchPositioning() {
          var location = matchCoordinates();
          if (location.x || location.y) {
            return {
              type: "position",
              value: location
            };
          }
        }
        function matchCoordinates() {
          return {
            x: matchDistance(),
            y: matchDistance()
          };
        }
        function matchListing(matcher) {
          var captures = matcher(), result = [];
          if (captures) {
            result.push(captures);
            while (scan(tokens.comma)) {
              captures = matcher();
              if (captures) {
                result.push(captures);
              } else {
                error("One extra comma");
              }
            }
          }
          return result;
        }
        function matchColorStop() {
          var color = matchColor();
          if (!color) {
            error("Expected color definition");
          }
          color.length = matchDistance();
          return color;
        }
        function matchColor() {
          return matchHexColor() || matchHSLAColor() || matchHSLColor() || matchRGBAColor() || matchRGBColor() || matchVarColor() || matchLiteralColor();
        }
        function matchLiteralColor() {
          return match("literal", tokens.literalColor, 0);
        }
        function matchHexColor() {
          return match("hex", tokens.hexColor, 1);
        }
        function matchRGBColor() {
          return matchCall(tokens.rgbColor, function() {
            return {
              type: "rgb",
              value: matchListing(matchNumber)
            };
          });
        }
        function matchRGBAColor() {
          return matchCall(tokens.rgbaColor, function() {
            return {
              type: "rgba",
              value: matchListing(matchNumber)
            };
          });
        }
        function matchVarColor() {
          return matchCall(tokens.varColor, function() {
            return {
              type: "var",
              value: matchVariableName()
            };
          });
        }
        function matchHSLColor() {
          return matchCall(tokens.hslColor, function() {
            var lookahead = scan(tokens.percentageValue);
            if (lookahead) {
              error("HSL hue value must be a number in degrees (0-360) or normalized (-360 to 360), not a percentage");
            }
            var hue = matchNumber();
            scan(tokens.comma);
            var captures = scan(tokens.percentageValue);
            var sat = captures ? captures[1] : null;
            scan(tokens.comma);
            captures = scan(tokens.percentageValue);
            var light = captures ? captures[1] : null;
            if (!sat || !light) {
              error("Expected percentage value for saturation and lightness in HSL");
            }
            return {
              type: "hsl",
              value: [hue, sat, light]
            };
          });
        }
        function matchHSLAColor() {
          return matchCall(tokens.hslaColor, function() {
            var hue = matchNumber();
            scan(tokens.comma);
            var captures = scan(tokens.percentageValue);
            var sat = captures ? captures[1] : null;
            scan(tokens.comma);
            captures = scan(tokens.percentageValue);
            var light = captures ? captures[1] : null;
            scan(tokens.comma);
            var alpha = matchNumber();
            if (!sat || !light) {
              error("Expected percentage value for saturation and lightness in HSLA");
            }
            return {
              type: "hsla",
              value: [hue, sat, light, alpha]
            };
          });
        }
        function matchPercentage() {
          var captures = scan(tokens.percentageValue);
          return captures ? captures[1] : null;
        }
        function matchVariableName() {
          return scan(tokens.variableName)[1];
        }
        function matchNumber() {
          return scan(tokens.number)[1];
        }
        function matchDistance() {
          return match("%", tokens.percentageValue, 1) || matchPositionKeyword() || matchCalc() || matchLength();
        }
        function matchPositionKeyword() {
          return match("position-keyword", tokens.positionKeywords, 1);
        }
        function matchCalc() {
          return matchCall(tokens.calcValue, function() {
            var openParenCount = 1;
            var i = 0;
            while (openParenCount > 0 && i < input.length) {
              var char = input.charAt(i);
              if (char === "(") {
                openParenCount++;
              } else if (char === ")") {
                openParenCount--;
              }
              i++;
            }
            if (openParenCount > 0) {
              error("Missing closing parenthesis in calc() expression");
            }
            var calcContent = input.substring(0, i - 1);
            consume(i - 1);
            return {
              type: "calc",
              value: calcContent
            };
          });
        }
        function matchLength() {
          return match("px", tokens.pixelValue, 1) || match("em", tokens.emValue, 1);
        }
        function match(type, pattern, captureIndex) {
          var captures = scan(pattern);
          if (captures) {
            return {
              type,
              value: captures[captureIndex]
            };
          }
        }
        function scan(regexp) {
          var captures, blankCaptures;
          blankCaptures = /^[\n\r\t\s]+/.exec(input);
          if (blankCaptures) {
            consume(blankCaptures[0].length);
          }
          captures = regexp.exec(input);
          if (captures) {
            consume(captures[0].length);
          }
          return captures;
        }
        function consume(size) {
          input = input.substr(size);
        }
        return function(code) {
          input = code.toString().trim();
          if (input.endsWith(";")) {
            input = input.slice(0, -1);
          }
          return getAST();
        };
      })();
      exports.parse = GradientParser.parse;
      exports.stringify = GradientParser.stringify;
    }
  });

  // node_modules/postcss/lib/postcss.mjs
  var import_postcss = __toESM(require_postcss(), 1);
  var stringify = import_postcss.default.stringify;
  var fromJSON = import_postcss.default.fromJSON;
  var plugin = import_postcss.default.plugin;
  var parse = import_postcss.default.parse;
  var list = import_postcss.default.list;
  var document2 = import_postcss.default.document;
  var comment = import_postcss.default.comment;
  var atRule = import_postcss.default.atRule;
  var rule = import_postcss.default.rule;
  var decl = import_postcss.default.decl;
  var root = import_postcss.default.root;
  var CssSyntaxError = import_postcss.default.CssSyntaxError;
  var Declaration = import_postcss.default.Declaration;
  var Container = import_postcss.default.Container;
  var Processor = import_postcss.default.Processor;
  var Document = import_postcss.default.Document;
  var Comment = import_postcss.default.Comment;
  var Warning = import_postcss.default.Warning;
  var AtRule = import_postcss.default.AtRule;
  var Result = import_postcss.default.Result;
  var Input = import_postcss.default.Input;
  var Rule = import_postcss.default.Rule;
  var Root = import_postcss.default.Root;
  var Node2 = import_postcss.default.Node;

  // node_modules/dom-to-svg/lib/index.js
  var import_postcss_value_parser4 = __toESM(require_lib(), 1);

  // node_modules/dom-to-svg/lib/css.js
  var isCSSFontFaceRule = (rule2) => rule2.type === CSSRule.FONT_FACE_RULE;
  var isInline = (styles) => styles.displayOutside === "inline" || styles.display.startsWith("inline-");
  var isPositioned = (styles) => styles.position !== "static";
  var isInFlow = (styles) => styles.float !== "none" && styles.position !== "absolute" && styles.position !== "fixed";
  var isTransparent = (color) => color === "transparent" || color === "rgba(0, 0, 0, 0)";
  var hasUniformBorder = (styles) => parseFloat(styles.borderTopWidth) !== 0 && styles.borderTopStyle !== "none" && styles.borderTopStyle !== "inset" && styles.borderTopStyle !== "outset" && !isTransparent(styles.borderTopColor) && // Cannot use border property directly as in Firefox those are empty strings.
  // Need to get the specific border properties from the specific sides.
  // https://stackoverflow.com/questions/41696063/getcomputedstyle-returns-empty-strings-on-ff-when-instead-crome-returns-a-comp
  styles.borderTopWidth === styles.borderLeftWidth && styles.borderTopWidth === styles.borderRightWidth && styles.borderTopWidth === styles.borderBottomWidth && styles.borderTopColor === styles.borderLeftColor && styles.borderTopColor === styles.borderRightColor && styles.borderTopColor === styles.borderBottomColor && styles.borderTopStyle === styles.borderLeftStyle && styles.borderTopStyle === styles.borderRightStyle && styles.borderTopStyle === styles.borderBottomStyle;
  var SIDES = ["top", "bottom", "right", "left"];
  var isHorizontal = (side) => side === "bottom" || side === "top";
  var CORNERS = {
    top: ["left", "right"],
    bottom: ["left", "right"],
    left: ["top", "bottom"],
    right: ["top", "bottom"]
  };
  function getBorderRadiiForSide(side, styles, bounds) {
    var _a, _b, _c, _d;
    const [horizontalStyle1, verticalStyle1] = styles.getPropertyValue(isHorizontal(side) ? `border-${side}-${CORNERS[side][0]}-radius` : `border-${CORNERS[side][0]}-${side}-radius`).split(" ");
    const [horizontalStyle2, verticalStyle2] = styles.getPropertyValue(isHorizontal(side) ? `border-${side}-${CORNERS[side][1]}-radius` : `border-${CORNERS[side][1]}-${side}-radius`).split(" ");
    if (isHorizontal(side)) {
      return [
        (_a = parseCSSLength(horizontalStyle1 || "0px", bounds.width)) !== null && _a !== void 0 ? _a : 0,
        (_b = parseCSSLength(horizontalStyle2 || "0px", bounds.width)) !== null && _b !== void 0 ? _b : 0
      ];
    }
    return [
      (_c = parseCSSLength(verticalStyle1 || horizontalStyle1 || "0px", bounds.height)) !== null && _c !== void 0 ? _c : 0,
      (_d = parseCSSLength(verticalStyle2 || horizontalStyle2 || "0px", bounds.height)) !== null && _d !== void 0 ? _d : 0
    ];
  }
  var calculateOverlappingCurvesFactor = (styles, bounds) => Math.min(...SIDES.map((side) => {
    const length = isHorizontal(side) ? bounds.width : bounds.height;
    const radiiSum = getBorderRadiiForSide(side, styles, bounds).reduce((sum, radius) => sum + radius, 0);
    return length / radiiSum;
  }), 1);
  var isVisible = (styles) => styles.displayOutside !== "none" && styles.display !== "none" && styles.visibility !== "hidden" && styles.opacity !== "0";
  function parseCSSLength(length, containerLength) {
    if (length.endsWith("px")) {
      return parseFloat(length);
    }
    if (length.endsWith("%")) {
      return parseFloat(length) / 100 * containerLength;
    }
    return void 0;
  }
  var unescapeStringValue = (value) => value.replace(/\\([\da-f]{1,2})/gi, (substring, codePoint) => String.fromCodePoint(parseInt(codePoint, 16))).replace(/\\(.)/g, "$1");
  function copyCssStyles(from, to) {
    for (const property of from) {
      to.setProperty(property, from.getPropertyValue(property), from.getPropertyPriority(property));
    }
  }

  // node_modules/dom-to-svg/lib/dom.js
  var svgNamespace = "http://www.w3.org/2000/svg";
  var xlinkNamespace = "http://www.w3.org/1999/xlink";
  var xhtmlNamespace = "http://www.w3.org/1999/xhtml";
  var isElement = (node) => node.nodeType === Node.ELEMENT_NODE;
  var isTextNode = (node) => node.nodeType === Node.TEXT_NODE;
  var isSVGElement = (element) => element.namespaceURI === svgNamespace;
  var isSVGSVGElement = (element) => isSVGElement(element) && element.tagName === "svg";
  var isSVGGraphicsElement = (element) => isSVGElement(element) && "getCTM" in element && "getScreenCTM" in element;
  var isSVGAnchorElement = (element) => isSVGElement(element) && element.tagName === "a";
  var isSVGTextContentElement = (element) => isSVGElement(element) && "textLength" in element;
  var isSVGImageElement = (element) => element.tagName === "image" && isSVGElement(element);
  var isSVGStyleElement = (element) => element.tagName === "style" && isSVGElement(element);
  var isHTMLElement = (element) => element.namespaceURI === xhtmlNamespace;
  var isHTMLAnchorElement = (element) => element.tagName === "A" && isHTMLElement(element);
  var isHTMLImageElement = (element) => element.tagName === "IMG" && isHTMLElement(element);
  var isHTMLInputElement = (element) => element.tagName === "INPUT" && isHTMLElement(element);
  var hasLabels = (element) => "labels" in element;

  // node_modules/dom-to-svg/lib/stacking.js
  var stackingContextEstablishingProperties = /* @__PURE__ */ new Set([
    "clipPath",
    "contain",
    "filter",
    "isolation",
    "mask",
    "maskBorder",
    "maskImage",
    "mixBlendMode",
    "opacity",
    "perspective",
    "position",
    "transform",
    "webkitOverflowScrolling",
    "zIndex"
  ]);
  function establishesStackingContext(styles, parentStyles) {
    return !!((styles.position === "absolute" || styles.position === "relative") && styles.zIndex !== "auto" || styles.position === "fixed" || styles.position === "sticky" || parentStyles && (parentStyles.display === "flex" || parentStyles.display === "grid") && styles.zIndex !== "auto" || parseFloat(styles.opacity) !== 1 || styles.mixBlendMode !== "normal" || styles.transform !== "none" || styles.filter !== "none" || styles.perspective !== "none" || styles.clipPath !== "none" || styles.mask !== "none" || styles.maskImage !== "none" || styles.maskBorder !== "none" || styles.isolation === "isolate" || styles.webkitOverflowScrolling === "touch" || styles.contain === "layout" || styles.contain === "paint" || styles.contain === "strict" || styles.contain === "content" || styles.willChange.split(",").some((property) => stackingContextEstablishingProperties.has(property.trim())));
  }
  var STACKING_LAYER_NAMES = [
    "rootBackgroundAndBorders",
    "childStackingContextsWithNegativeStackLevels",
    "inFlowNonInlineNonPositionedDescendants",
    "nonPositionedFloats",
    "inFlowInlineLevelNonPositionedDescendants",
    "childStackingContextsWithStackLevelZeroAndPositionedDescendantsWithStackLevelZero",
    "childStackingContextsWithPositiveStackLevels"
  ];
  function createStackingLayer(parent, layerName) {
    const layer = parent.ownerDocument.createElementNS(svgNamespace, "g");
    layer.dataset.stackingLayer = layerName;
    parent.append(layer);
    return layer;
  }
  function createStackingLayers(container) {
    container.dataset.stackingContext = "true";
    return {
      rootBackgroundAndBorders: createStackingLayer(container, "rootBackgroundAndBorders"),
      childStackingContextsWithNegativeStackLevels: createStackingLayer(container, "childStackingContextsWithNegativeStackLevels"),
      inFlowNonInlineNonPositionedDescendants: createStackingLayer(container, "inFlowNonInlineNonPositionedDescendants"),
      nonPositionedFloats: createStackingLayer(container, "nonPositionedFloats"),
      inFlowInlineLevelNonPositionedDescendants: createStackingLayer(container, "inFlowInlineLevelNonPositionedDescendants"),
      childStackingContextsWithStackLevelZeroAndPositionedDescendantsWithStackLevelZero: createStackingLayer(container, "childStackingContextsWithStackLevelZeroAndPositionedDescendantsWithStackLevelZero"),
      childStackingContextsWithPositiveStackLevels: createStackingLayer(container, "childStackingContextsWithPositiveStackLevels")
    };
  }
  function determineStackingLayer(styles, parentStyles) {
    const zIndex = styles.zIndex !== "auto" ? parseInt(styles.zIndex, 10) : void 0;
    if (zIndex !== void 0 && zIndex < 0 && establishesStackingContext(styles, parentStyles)) {
      return "childStackingContextsWithNegativeStackLevels";
    }
    if (isInFlow(styles) && !isInline(styles) && !isPositioned(styles)) {
      return "inFlowNonInlineNonPositionedDescendants";
    }
    if (!isPositioned(styles) && styles.float !== "none") {
      return "nonPositionedFloats";
    }
    if (isInFlow(styles) && isInline(styles) && !isPositioned(styles)) {
      return "inFlowInlineLevelNonPositionedDescendants";
    }
    if (zIndex === 0 && (isPositioned(styles) || establishesStackingContext(styles, parentStyles))) {
      return "childStackingContextsWithStackLevelZeroAndPositionedDescendantsWithStackLevelZero";
    }
    if (zIndex !== void 0 && zIndex > 0 && establishesStackingContext(styles, parentStyles)) {
      return "childStackingContextsWithPositiveStackLevels";
    }
    return void 0;
  }
  function sortChildrenByZIndex(parent) {
    const sorted = [...parent.children].sort((a, b) => {
      const zIndexA = a.dataset.zIndex;
      const zIndexB = b.dataset.zIndex;
      if (!zIndexA || !zIndexB) {
        return 0;
      }
      return parseInt(zIndexA, 10) - parseInt(zIndexB, 10);
    });
    for (const child of sorted) {
      parent.append(child);
    }
  }
  function sortStackingLayerChildren(stackingLayers) {
    sortChildrenByZIndex(stackingLayers.childStackingContextsWithNegativeStackLevels);
    sortChildrenByZIndex(stackingLayers.childStackingContextsWithPositiveStackLevels);
  }
  function cleanupStackingLayerChildren(stackingLayers) {
    for (const name of STACKING_LAYER_NAMES) {
      const layer = stackingLayers[name];
      if (!layer.hasChildNodes()) {
        layer.remove();
      }
    }
  }

  // node_modules/dom-to-svg/lib/element.js
  var import_postcss_value_parser2 = __toESM(require_lib(), 1);

  // node_modules/dom-to-svg/lib/accessibility.js
  var isStandaloneFooter = (element) => !element.closest('article, aside, main, nav, section, [role="article"], [role="complementary"], [role="main"], [role="navigation"], [role="region"]');
  function getAccessibilityAttributes(element, { labels, getUniqueId }) {
    var _a, _b, _c;
    const attributes = /* @__PURE__ */ new Map();
    switch (element.tagName) {
      case "A":
        attributes.set("role", "link");
        break;
      case "ARTICLE":
        attributes.set("role", "article");
        break;
      case "ASIDE":
        attributes.set("role", "complementary");
        break;
      case "BODY":
        attributes.set("role", "document");
        break;
      case "BUTTON":
      case "SUMMARY":
        attributes.set("role", "button");
        break;
      case "DD":
        attributes.set("role", "definition");
        break;
      case "DETAILS":
        attributes.set("role", "group");
        break;
      case "DFN":
        attributes.set("role", "term");
        break;
      case "DIALOG":
        attributes.set("role", "dialog");
        break;
      case "DT":
        attributes.set("role", "term");
        break;
      case "FIELDSET":
        attributes.set("role", "group");
        break;
      case "FIGURE":
        attributes.set("role", "figure");
        break;
      case "FOOTER":
        if (isStandaloneFooter(element)) {
          attributes.set("role", "contentinfo");
        }
        break;
      case "FORM":
        attributes.set("role", "form");
        break;
      case "H1":
      case "H2":
      case "H3":
      case "H4":
      case "H5":
      case "H6":
        attributes.set("role", "heading");
        attributes.set("aria-level", element.tagName.slice(1));
        break;
      case "HEADER":
        if (isStandaloneFooter(element)) {
          attributes.set("role", "banner");
        }
        break;
      case "HR":
        attributes.set("role", "separator");
        break;
      case "IMG": {
        const alt = element.getAttribute("alt");
        if (alt === null || alt !== "") {
          attributes.set("role", "img");
          if (alt) {
            attributes.set("aria-label", alt);
          }
        }
        break;
      }
      case "INPUT":
        switch (element.type) {
          case "button":
          case "image":
          case "reset":
          case "submit":
            attributes.set("role", "button");
            break;
          case "number":
            attributes.set("role", "spinbutton");
            break;
          case "range":
            attributes.set("role", "slider");
            break;
          case "checkbox":
            attributes.set("role", "checkbox");
            break;
          case "radio":
            attributes.set("role", "radio");
            break;
          case "email":
          case "tel":
            if (!element.hasAttribute("list")) {
              attributes.set("role", "textbox");
            }
            break;
        }
        break;
      case "LI":
        if (((_a = element.parentElement) === null || _a === void 0 ? void 0 : _a.tagName) === "OL" || ((_b = element.parentElement) === null || _b === void 0 ? void 0 : _b.tagName) === "UL" || ((_c = element.parentElement) === null || _c === void 0 ? void 0 : _c.tagName) === "MENU") {
          attributes.set("role", "listitem");
        }
        break;
      case "LINK":
        if (element.href) {
          attributes.set("role", "link");
        }
        break;
      case "MAIN":
        attributes.set("role", "main");
        break;
      case "MATH":
        attributes.set("role", "math");
        break;
      case "OL":
      case "UL":
      case "MENU":
        attributes.set("role", "list");
        break;
      case "NAV":
        attributes.set("role", "navigation");
        break;
      case "OPTION":
        attributes.set("role", "option");
        break;
      case "PROGRESS":
        attributes.set("role", "progressbar");
        break;
      case "SECTION":
        attributes.set("role", "region");
        break;
      case "SELECT":
        attributes.set("role", !element.hasAttribute("multiple") && element.size <= 1 ? "combobox" : "listbox");
        break;
      case "TABLE":
        attributes.set("role", "table");
        break;
      case "THEAD":
      case "TBODY":
      case "TFOOT":
        attributes.set("role", "rowgroup");
        break;
      case "TEXTAREA":
        attributes.set("role", "textbox");
        break;
      case "TD":
        attributes.set("role", "cell");
        break;
      case "TH":
        attributes.set("role", element.closest("thead") ? "columnheader" : "rowheader");
        break;
      case "TR":
        attributes.set("role", "tablerow");
        break;
    }
    if (element.hasAttribute("disabled")) {
      attributes.set("aria-disabled", "true");
    }
    if (element.hasAttribute("placeholder")) {
      attributes.set("aria-placeholder", element.getAttribute("placeholder") || "");
    }
    const tabIndex = element.getAttribute("tabindex");
    if (tabIndex) {
      attributes.set("tabindex", tabIndex);
    }
    if (isHTMLElement(element) && hasLabels(element) && element.labels) {
      attributes.set("aria-labelledby", [...element.labels].map((label) => {
        let labelId = label.id || labels.get(label);
        if (!labelId) {
          labelId = getUniqueId("label");
          labels.set(label, labelId);
        }
        return labelId;
      }).join(" "));
    }
    for (const attribute of element.attributes) {
      if (attribute.name.startsWith("aria-")) {
        attributes.set(attribute.name, attribute.value);
      }
    }
    const customRole = element.getAttribute("role");
    if (customRole) {
      attributes.set("role", customRole);
    }
    return attributes;
  }

  // node_modules/dom-to-svg/lib/gradients.js
  var gradientParser = __toESM(require_node2(), 1);
  var positionsForOrientation = (orientation) => {
    const positions = {
      x1: "0%",
      x2: "0%",
      y1: "0%",
      y2: "0%"
    };
    if ((orientation === null || orientation === void 0 ? void 0 : orientation.type) === "angular") {
      const anglePI = orientation.value * (Math.PI / 180);
      positions.x1 = `${Math.round(50 + Math.sin(anglePI + Math.PI) * 50)}%`;
      positions.y1 = `${Math.round(50 + Math.cos(anglePI) * 50)}%`;
      positions.x2 = `${Math.round(50 + Math.sin(anglePI) * 50)}%`;
      positions.y2 = `${Math.round(50 + Math.cos(anglePI + Math.PI) * 50)}%`;
    } else if ((orientation === null || orientation === void 0 ? void 0 : orientation.type) === "directional") {
      switch (orientation.value) {
        case "left":
          positions.x1 = "100%";
          break;
        case "top":
          positions.y1 = "100%";
          break;
        case "right":
          positions.x2 = "100%";
          break;
        case "bottom":
          positions.y2 = "100%";
          break;
      }
    }
    return positions;
  };
  function convertLinearGradient(css, { svgDocument }) {
    const { orientation, colorStops } = gradientParser.parse(css)[0];
    const { x1, x2, y1, y2 } = positionsForOrientation(orientation);
    const getColorStops = (colorStop, index) => {
      const offset = `${index / (colorStops.length - 1) * 100}%`;
      let stopColor = "rgb(0,0,0)";
      let stopOpacity = 1;
      switch (colorStop.type) {
        case "rgb": {
          const [red, green, blue] = colorStop.value;
          stopColor = `rgb(${red},${green},${blue})`;
          break;
        }
        case "rgba": {
          const [red, green, blue, alpha] = colorStop.value;
          stopColor = `rgb(${red},${green},${blue})`;
          stopOpacity = alpha;
          break;
        }
        case "hex": {
          stopColor = `#${colorStop.value}`;
          break;
        }
        case "literal": {
          stopColor = colorStop.value;
          break;
        }
      }
      const stop = svgDocument.createElementNS(svgNamespace, "stop");
      stop.setAttribute("offset", offset);
      stop.setAttribute("stop-color", stopColor);
      stop.setAttribute("stop-opacity", stopOpacity.toString());
      return stop;
    };
    const linearGradient = svgDocument.createElementNS(svgNamespace, "linearGradient");
    linearGradient.setAttribute("x1", x1);
    linearGradient.setAttribute("y1", y1);
    linearGradient.setAttribute("x2", x2);
    linearGradient.setAttribute("y2", y2);
    linearGradient.append(...colorStops.map(getColorStops));
    return linearGradient;
  }

  // node_modules/dom-to-svg/lib/svg.js
  var import_postcss_value_parser = __toESM(require_lib(), 1);

  // node_modules/dom-to-svg/lib/util.js
  var createIdGenerator = () => {
    const nextCounts = /* @__PURE__ */ new Map();
    return (prefix) => {
      var _a;
      const count = (_a = nextCounts.get(prefix)) !== null && _a !== void 0 ? _a : 1;
      nextCounts.set(prefix, count + 1);
      return `${prefix}${count}`;
    };
  };
  var doRectanglesIntersect = (a, b) => !(a.bottom < b.top || // A is above B
  a.top > b.bottom || // A is below B
  a.right < b.left || // A is left of B
  // A is right of B
  a.left > b.right);
  function diagonale(box) {
    return Math.sqrt(box.width ** 2 + box.height ** 2);
  }
  function withTimeout(timeout, message, func) {
    return Promise.race([
      func(),
      new Promise((resolve, reject) => setTimeout(() => reject(new Error(message)), timeout))
    ]);
  }
  var isTaggedUnionMember = (key, value) => (object) => object[key] === value;
  function assert(condition, message) {
    if (!condition) {
      throw new Error(message);
    }
  }

  // node_modules/dom-to-svg/lib/text.js
  function handleTextNode(textNode, context) {
    if (!textNode.ownerDocument.defaultView) {
      throw new Error("Element's ownerDocument has no defaultView");
    }
    const window2 = textNode.ownerDocument.defaultView;
    const parentElement = textNode.parentElement;
    const styles = window2.getComputedStyle(parentElement);
    if (!isVisible(styles)) {
      return;
    }
    const selection = window2.getSelection();
    assert(selection, "Could not obtain selection from window. Selection is needed for detecting whitespace collapsing in text.");
    const svgTextElement = context.svgDocument.createElementNS(svgNamespace, "text");
    copyTextStyles(styles, svgTextElement);
    const tabSize = parseInt(styles.tabSize, 10);
    svgTextElement.setAttribute("dominant-baseline", "text-after-edge");
    const lineRange = textNode.ownerDocument.createRange();
    lineRange.setStart(textNode, 0);
    lineRange.setEnd(textNode, 0);
    while (true) {
      const addTextSpanForLineRange = () => {
        if (lineRange.collapsed) {
          return;
        }
        const lineRectangle = lineRange.getClientRects()[0];
        if (!doRectanglesIntersect(lineRectangle, context.options.captureArea)) {
          return;
        }
        const textSpan = context.svgDocument.createElementNS(svgNamespace, "tspan");
        textSpan.setAttribute("xml:space", "preserve");
        const previousUserSelect = parentElement.style.userSelect;
        parentElement.style.userSelect = "all";
        try {
          selection.removeAllRanges();
          selection.addRange(lineRange);
          textSpan.textContent = selection.toString().replace(/\t/g, " ".repeat(tabSize));
        } finally {
          parentElement.style.userSelect = previousUserSelect;
          selection.removeAllRanges();
        }
        textSpan.setAttribute("x", lineRectangle.x.toString());
        textSpan.setAttribute("y", lineRectangle.bottom.toString());
        textSpan.setAttribute("textLength", lineRectangle.width.toString());
        textSpan.setAttribute("lengthAdjust", "spacingAndGlyphs");
        svgTextElement.append(textSpan);
      };
      try {
        lineRange.setEnd(textNode, lineRange.endOffset + 1);
      } catch (error) {
        if (error.code === DOMException.INDEX_SIZE_ERR) {
          addTextSpanForLineRange();
          break;
        }
        throw error;
      }
      const lineRectangles = lineRange.getClientRects();
      if (!lineRectangles[0]) {
        return;
      }
      if (lineRectangles[1] && lineRectangles[0].top !== lineRectangles[1].top) {
        lineRange.setEnd(textNode, lineRange.endOffset - 1);
        addTextSpanForLineRange();
        lineRange.setStart(textNode, lineRange.endOffset);
      }
    }
    context.currentSvgParent.append(svgTextElement);
  }
  var textAttributes = /* @__PURE__ */ new Set([
    "color",
    "dominant-baseline",
    "font-family",
    "font-size",
    "font-size-adjust",
    "font-stretch",
    "font-style",
    "font-variant",
    "font-weight",
    "direction",
    "letter-spacing",
    "text-decoration",
    "text-anchor",
    "text-decoration",
    "text-rendering",
    "unicode-bidi",
    "word-spacing",
    "writing-mode",
    "user-select"
  ]);
  function copyTextStyles(styles, svgElement) {
    for (const textProperty of textAttributes) {
      const value = styles.getPropertyValue(textProperty);
      if (value) {
        svgElement.setAttribute(textProperty, value);
      }
    }
    svgElement.setAttribute("fill", styles.color);
  }

  // node_modules/dom-to-svg/lib/svg.js
  function handleSvgNode(node, context) {
    if (isElement(node)) {
      if (!isSVGElement(node)) {
        return;
      }
      handleSvgElement(node, context);
    } else if (isTextNode(node)) {
      const clonedTextNode = node.cloneNode(true);
      context.currentSvgParent.append(clonedTextNode);
    }
  }
  var ignoredElements = /* @__PURE__ */ new Set(["script", "style", "foreignElement"]);
  var URL_ID_REFERENCE_REGEX = /\burl\(["']?#/;
  function handleSvgElement(element, context) {
    var _a, _b, _c, _d;
    if (ignoredElements.has(element.tagName)) {
      return;
    }
    let elementToAppend;
    if (isSVGSVGElement(element)) {
      const contentContainer = context.svgDocument.createElementNS(svgNamespace, "g");
      elementToAppend = contentContainer;
      contentContainer.classList.add("svg-content", ...element.classList);
      contentContainer.dataset.viewBox = (_a = element.getAttribute("viewBox")) !== null && _a !== void 0 ? _a : "";
      contentContainer.dataset.width = (_b = element.getAttribute("width")) !== null && _b !== void 0 ? _b : "";
      contentContainer.dataset.height = (_c = element.getAttribute("height")) !== null && _c !== void 0 ? _c : "";
      for (const child of element.children) {
        if (!isSVGGraphicsElement(child)) {
          continue;
        }
        let viewBoxTransformMatrix = (
          // When this function is called on an inline <svg> element in the original DOM, we want
          // getScreenCTM() to map it to the DOM coordinate system. When this function is called from
          // inlineResources() the <svg> is already embedded into the output <svg>. In that case the output
          // SVG already has a viewBox, and the coordinate system of the SVG is not equal to the coordinate
          // system of the screen, therefor we need to use getCTM() to map it into the output SVG's
          // coordinate system.
          child.ownerDocument !== context.svgDocument && // When we inline an SVG, we put a transform on it for the getScreenCTM(). When that SVG also
          // contains another SVG, the inner SVG should just get transformed relative to the outer SVG, not
          // relative to the screen, because the transforms will stack in the output SVG.
          !((_d = element.parentElement) === null || _d === void 0 ? void 0 : _d.closest("svg")) ? child.getScreenCTM() : child.getCTM()
        );
        if (!viewBoxTransformMatrix) {
          break;
        }
        if (child.transform.baseVal.numberOfItems > 0) {
          child.transform.baseVal.consolidate();
          const existingTransform = child.transform.baseVal.getItem(0).matrix;
          viewBoxTransformMatrix = viewBoxTransformMatrix.multiply(existingTransform.inverse());
        }
        contentContainer.transform.baseVal.appendItem(contentContainer.transform.baseVal.createSVGTransformFromMatrix(viewBoxTransformMatrix));
        break;
      }
    } else {
      if (isSVGAnchorElement(element) && !context.options.keepLinks) {
        elementToAppend = context.svgDocument.createElementNS(svgNamespace, "g");
      } else {
        elementToAppend = element.cloneNode(false);
      }
      for (const attribute of elementToAppend.attributes) {
        if (attribute.localName.startsWith("on")) {
          elementToAppend.attributes.removeNamedItemNS(attribute.namespaceURI, attribute.localName);
        } else if (attribute.localName === "href" && attribute.value.startsWith("javascript:")) {
          elementToAppend.attributes.removeNamedItemNS(attribute.namespaceURI, attribute.localName);
        }
      }
      const window2 = element.ownerDocument.defaultView;
      assert(window2, "Element's ownerDocument has no defaultView");
      const svgViewportElement = element.ownerSVGElement;
      assert(svgViewportElement, "Expected element to have ownerSVGElement");
      const styles = window2.getComputedStyle(element);
      if (isSVGGraphicsElement(element)) {
        copyGraphicalPresentationAttributes(styles, elementToAppend, svgViewportElement.viewBox.animVal);
        if (isSVGTextContentElement(element)) {
          copyTextStyles(styles, elementToAppend);
        }
      }
      for (const attribute of elementToAppend.attributes) {
        if (attribute.localName === "href") {
          if (attribute.value.startsWith("#")) {
            attribute.value = attribute.value.replace("#", `#${context.idPrefix}`);
          }
        } else if (URL_ID_REFERENCE_REGEX.test(attribute.value)) {
          attribute.value = rewriteUrlIdReferences(attribute.value, context);
        }
      }
      for (const property of elementToAppend.style) {
        const value = elementToAppend.style.getPropertyValue(property);
        if (URL_ID_REFERENCE_REGEX.test(value)) {
          elementToAppend.style.setProperty(property, rewriteUrlIdReferences(value, context), elementToAppend.style.getPropertyPriority(property));
        }
      }
    }
    if (elementToAppend.id) {
      elementToAppend.id = context.idPrefix + elementToAppend.id;
    }
    context.currentSvgParent.append(elementToAppend);
    for (const child of element.childNodes) {
      handleSvgNode(child, { ...context, currentSvgParent: elementToAppend });
    }
  }
  var graphicalPresentationAttributes = [
    "alignment-baseline",
    "baseline-shift",
    // 'clip',
    "clip-path",
    "clip-rule",
    "color",
    "color-interpolation",
    "color-interpolation-filters",
    // 'color-profile',
    "color-rendering",
    // 'cursor',
    "direction",
    // 'display',
    // 'enable-background',
    "fill",
    "fill-opacity",
    "fill-rule",
    "filter",
    "flood-color",
    "flood-opacity",
    "image-rendering",
    "lighting-color",
    "marker-end",
    "marker-mid",
    "marker-start",
    "mask",
    "opacity",
    // 'overflow',
    "pointer-events",
    "shape-rendering",
    // 'solid-color',
    // 'solid-opacity',
    "stop-color",
    "stop-opacity",
    "stroke",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "transform",
    "vector-effect",
    "visibility"
  ];
  var defaults = {
    "alignment-baseline": "auto",
    "baseline-shift": "0px",
    "clip-path": "none",
    "clip-rule": "nonzero",
    "color-interpolation-filters": "linearrgb",
    "color-interpolation": "srgb",
    "color-rendering": "auto",
    "fill-opacity": "1",
    "fill-rule": "nonzero",
    "flood-color": "rgb(0, 0, 0)",
    "flood-opacity": "1",
    "image-rendering": "auto",
    "lighting-color": "rgb(255, 255, 255)",
    "marker-end": "none",
    "marker-mid": "none",
    "marker-start": "none",
    "pointer-events": "auto",
    "shape-rendering": "auto",
    "stop-color": "rgb(0, 0, 0)",
    "stop-opacity": "1",
    "stroke-dasharray": "none",
    "stroke-dashoffset": "0px",
    "stroke-linecap": "butt",
    "stroke-linejoin": "miter",
    "stroke-miterlimit": "4",
    "stroke-opacity": "1",
    "stroke-width": "1px",
    "vector-effect": "none",
    color: "",
    direction: "ltr",
    fill: "",
    filter: "none",
    mask: "none",
    opacity: "1",
    stroke: "",
    transform: "none",
    visibility: "visible"
  };
  function rewriteUrlIdReferences(value, { idPrefix }) {
    const parsedValue = (0, import_postcss_value_parser.default)(value);
    parsedValue.walk((node) => {
      if (node.type !== "function" || node.value !== "url") {
        return;
      }
      const urlArgument = node.nodes[0];
      if (!urlArgument) {
        return;
      }
      urlArgument.value = urlArgument.value.replace("#", `#${idPrefix}`);
    });
    return import_postcss_value_parser.default.stringify(parsedValue.nodes);
  }
  function copyGraphicalPresentationAttributes(styles, target, viewBox) {
    var _a;
    for (const attribute of graphicalPresentationAttributes) {
      let value = styles.getPropertyValue(attribute);
      if (value && value !== defaults[attribute]) {
        if (value.endsWith("%")) {
          value = (_a = parseCSSLength(value, diagonale(viewBox))) !== null && _a !== void 0 ? _a : 0;
        }
        target.setAttribute(attribute, value.toString());
      }
    }
  }

  // node_modules/dom-to-svg/lib/element.js
  function handleElement(element, context) {
    var _a, _b, _c, _d, _e, _f, _g;
    const cleanupFunctions = [];
    try {
      const window2 = element.ownerDocument.defaultView;
      if (!window2) {
        throw new Error("Element's ownerDocument has no defaultView");
      }
      const bounds = element.getBoundingClientRect();
      const rectanglesIntersect = doRectanglesIntersect(bounds, context.options.captureArea);
      const styles = window2.getComputedStyle(element);
      const parentStyles = element.parentElement && window2.getComputedStyle(element.parentElement);
      const svgContainer = isHTMLAnchorElement(element) && context.options.keepLinks ? createSvgAnchor(element, context) : context.svgDocument.createElementNS(svgNamespace, "g");
      svgContainer.dataset.tag = element.tagName.toLowerCase();
      const id = element.id || context.getUniqueId(element.classList[0] || element.tagName.toLowerCase());
      svgContainer.id = id;
      const className = element.getAttribute("class");
      if (className) {
        svgContainer.setAttribute("class", className);
      }
      if (isHTMLElement(element) && element.title) {
        const svgTitle = context.svgDocument.createElementNS(svgNamespace, "title");
        svgTitle.textContent = element.title;
        svgContainer.prepend(svgTitle);
      }
      const stackingLayerName = determineStackingLayer(styles, parentStyles);
      const stackingLayer = stackingLayerName ? context.stackingLayers[stackingLayerName] : context.parentStackingLayer;
      if (stackingLayer) {
        context.currentSvgParent.setAttribute("aria-owns", [context.currentSvgParent.getAttribute("aria-owns"), svgContainer.id].filter(Boolean).join(" "));
      }
      const elementToAppendTo = context.parentStackingLayer === stackingLayer ? context.currentSvgParent : stackingLayer;
      svgContainer.dataset.zIndex = styles.zIndex;
      elementToAppendTo.append(svgContainer);
      let childContext;
      let backgroundContainer;
      let ownStackingLayers;
      if (establishesStackingContext(styles, parentStyles)) {
        ownStackingLayers = createStackingLayers(svgContainer);
        backgroundContainer = ownStackingLayers.rootBackgroundAndBorders;
        childContext = {
          ...context,
          currentSvgParent: svgContainer,
          stackingLayers: ownStackingLayers,
          parentStackingLayer: stackingLayer
        };
      } else {
        backgroundContainer = svgContainer;
        childContext = {
          ...context,
          currentSvgParent: svgContainer,
          parentStackingLayer: stackingLayer
        };
      }
      if (styles.opacity !== "1") {
        svgContainer.setAttribute("opacity", styles.opacity);
      }
      for (const [name, value] of getAccessibilityAttributes(element, context)) {
        svgContainer.setAttribute(name, value);
      }
      if (isHTMLElement(element) && !element.dataset.pseudoElement) {
        const handlePseudoElement = (pseudoSelector, position) => {
          const pseudoElementStyles = window2.getComputedStyle(element, pseudoSelector);
          const content = (0, import_postcss_value_parser2.default)(pseudoElementStyles.content).nodes.find(isTaggedUnionMember("type", "string"));
          if (!content) {
            return;
          }
          const span = element.ownerDocument.createElement("span");
          span.dataset.pseudoElement = pseudoSelector;
          copyCssStyles(pseudoElementStyles, span.style);
          span.textContent = unescapeStringValue(content.value);
          element.dataset.pseudoElementOwner = id;
          cleanupFunctions.push(() => element.removeAttribute("data-pseudo-element-owner"));
          const style = element.ownerDocument.createElement("style");
          style.textContent = `[data-pseudo-element-owner="${id}"]${pseudoSelector} { display: none !important; }`;
          element.before(style);
          cleanupFunctions.push(() => style.remove());
          element[position](span);
          cleanupFunctions.push(() => span.remove());
        };
        handlePseudoElement("::before", "prepend");
        handlePseudoElement("::after", "append");
      }
      if (rectanglesIntersect) {
        addBackgroundAndBorders(styles, bounds, backgroundContainer, window2, context);
      }
      if (styles.overflow !== "visible") {
        const mask = context.svgDocument.createElementNS(svgNamespace, "mask");
        mask.id = context.getUniqueId("mask-for-" + id);
        const visibleRectangle = createBox(bounds, context);
        visibleRectangle.setAttribute("fill", "#ffffff");
        mask.append(visibleRectangle);
        svgContainer.append(mask);
        svgContainer.setAttribute("mask", `url(#${mask.id})`);
        childContext = {
          ...childContext,
          ancestorMasks: [{ mask, forElement: element }, ...childContext.ancestorMasks]
        };
      }
      if (isHTMLElement(element) && (styles.position === "absolute" || styles.position === "fixed") && context.ancestorMasks.length > 0 && element.offsetParent) {
        for (const { mask, forElement } of context.ancestorMasks) {
          if (element.offsetParent.contains(forElement) || element.offsetParent === forElement) {
            const visibleRectangle = createBox(bounds, context);
            visibleRectangle.setAttribute("fill", "#ffffff");
            mask.append(visibleRectangle);
          } else {
            break;
          }
        }
      }
      if (rectanglesIntersect && isHTMLImageElement(element) && // Make sure the element has a src/srcset attribute (the relative URL). `element.src` is absolute and always defined.
      (element.getAttribute("src") || element.getAttribute("srcset"))) {
        const svgImage = context.svgDocument.createElementNS(svgNamespace, "image");
        svgImage.id = `${id}-image`;
        svgImage.setAttribute("xlink:href", element.currentSrc || element.src);
        const paddingLeft = (_a = parseCSSLength(styles.paddingLeft, bounds.width)) !== null && _a !== void 0 ? _a : 0;
        const paddingRight = (_b = parseCSSLength(styles.paddingRight, bounds.width)) !== null && _b !== void 0 ? _b : 0;
        const paddingTop = (_c = parseCSSLength(styles.paddingTop, bounds.height)) !== null && _c !== void 0 ? _c : 0;
        const paddingBottom = (_d = parseCSSLength(styles.paddingBottom, bounds.height)) !== null && _d !== void 0 ? _d : 0;
        svgImage.setAttribute("x", (bounds.x + paddingLeft).toString());
        svgImage.setAttribute("y", (bounds.y + paddingTop).toString());
        svgImage.setAttribute("width", (bounds.width - paddingLeft - paddingRight).toString());
        svgImage.setAttribute("height", (bounds.height - paddingTop - paddingBottom).toString());
        if (element.alt) {
          svgImage.setAttribute("aria-label", element.alt);
        }
        svgContainer.append(svgImage);
      } else if (rectanglesIntersect && isHTMLInputElement(element) && bounds.width > 0 && bounds.height > 0) {
        if (element.value) {
          const svgTextElement = context.svgDocument.createElementNS(svgNamespace, "text");
          copyTextStyles(styles, svgTextElement);
          svgTextElement.setAttribute("dominant-baseline", "central");
          svgTextElement.setAttribute("xml:space", "preserve");
          svgTextElement.setAttribute("x", (bounds.x + ((_e = parseCSSLength(styles.paddingLeft, bounds.width)) !== null && _e !== void 0 ? _e : 0)).toString());
          const top = bounds.top + ((_f = parseCSSLength(styles.paddingTop, bounds.height)) !== null && _f !== void 0 ? _f : 0);
          const bottom = bounds.bottom + ((_g = parseCSSLength(styles.paddingBottom, bounds.height)) !== null && _g !== void 0 ? _g : 0);
          const middle = (top + bottom) / 2;
          svgTextElement.setAttribute("y", middle.toString());
          svgTextElement.textContent = element.value;
          childContext.stackingLayers.inFlowInlineLevelNonPositionedDescendants.append(svgTextElement);
        }
      } else if (rectanglesIntersect && isSVGSVGElement(element) && isVisible(styles)) {
        handleSvgNode(element, { ...childContext, idPrefix: `${id}-` });
      } else {
        for (const child of element.childNodes) {
          walkNode(child, childContext);
        }
        if (ownStackingLayers) {
          sortStackingLayerChildren(ownStackingLayers);
          cleanupStackingLayerChildren(ownStackingLayers);
        }
      }
    } finally {
      for (const cleanup of cleanupFunctions) {
        cleanup();
      }
    }
  }
  function addBackgroundAndBorders(styles, bounds, backgroundAndBordersContainer, window2, context) {
    var _a, _b, _c, _d;
    if (isVisible(styles)) {
      if (bounds.width > 0 && bounds.height > 0 && (!isTransparent(styles.backgroundColor) || hasUniformBorder(styles) || styles.backgroundImage !== "none")) {
        const box = createBackgroundAndBorderBox(bounds, styles, context);
        backgroundAndBordersContainer.append(box);
        if (styles.backgroundImage !== "none") {
          const backgrounds = (0, import_postcss_value_parser2.default)(styles.backgroundImage).nodes.filter(isTaggedUnionMember("type", "function")).reverse();
          const xBackgroundPositions = styles.backgroundPositionX.split(/\s*,\s*/g);
          const yBackgroundPositions = styles.backgroundPositionY.split(/\s*,\s*/g);
          const backgroundRepeats = styles.backgroundRepeat.split(/\s*,\s*/g);
          for (const [index, backgroundNode] of backgrounds.entries()) {
            const backgroundPositionX = (_a = parseCSSLength(xBackgroundPositions[index], bounds.width)) !== null && _a !== void 0 ? _a : 0;
            const backgroundPositionY = (_b = parseCSSLength(yBackgroundPositions[index], bounds.height)) !== null && _b !== void 0 ? _b : 0;
            const backgroundRepeat = backgroundRepeats[index];
            if (backgroundNode.value === "url" && backgroundNode.nodes[0]) {
              const urlArgument = backgroundNode.nodes[0];
              const image = context.svgDocument.createElementNS(svgNamespace, "image");
              image.id = context.getUniqueId("background-image");
              const [cssWidth = "auto", cssHeight = "auto"] = styles.backgroundSize.split(" ");
              const backgroundWidth = (_c = parseCSSLength(cssWidth, bounds.width)) !== null && _c !== void 0 ? _c : bounds.width;
              const backgroundHeight = (_d = parseCSSLength(cssHeight, bounds.height)) !== null && _d !== void 0 ? _d : bounds.height;
              image.setAttribute("width", backgroundWidth.toString());
              image.setAttribute("height", backgroundHeight.toString());
              if (cssWidth !== "auto" && cssHeight !== "auto") {
                image.setAttribute("preserveAspectRatio", "none");
              } else if (styles.backgroundSize === "contain") {
                image.setAttribute("preserveAspectRatio", "xMidYMid meet");
              } else if (styles.backgroundSize === "cover") {
                image.setAttribute("preserveAspectRatio", "xMidYMid slice");
              }
              const url = new URL(unescapeStringValue(urlArgument.value), window2.location.href);
              image.setAttribute("xlink:href", url.href);
              if (backgroundRepeat === "no-repeat" || backgroundPositionX === 0 && backgroundPositionY === 0 && backgroundWidth === bounds.width && backgroundHeight === bounds.height) {
                image.setAttribute("x", bounds.x.toString());
                image.setAttribute("y", bounds.y.toString());
                backgroundAndBordersContainer.append(image);
              } else {
                image.setAttribute("x", "0");
                image.setAttribute("y", "0");
                const pattern = context.svgDocument.createElementNS(svgNamespace, "pattern");
                pattern.setAttribute("patternUnits", "userSpaceOnUse");
                pattern.setAttribute("patternContentUnits", "userSpaceOnUse");
                pattern.setAttribute("x", (bounds.x + backgroundPositionX).toString());
                pattern.setAttribute("y", (bounds.y + backgroundPositionY).toString());
                pattern.setAttribute("width", (backgroundRepeat === "repeat" || backgroundRepeat === "repeat-x" ? backgroundWidth : (
                  // If background shouldn't repeat on this axis, make the tile as big as the element so the repetition is cut off.
                  backgroundWidth + bounds.x + backgroundPositionX
                )).toString());
                pattern.setAttribute("height", (backgroundRepeat === "repeat" || backgroundRepeat === "repeat-y" ? backgroundHeight : (
                  // If background shouldn't repeat on this axis, make the tile as big as the element so the repetition is cut off.
                  backgroundHeight + bounds.y + backgroundPositionY
                )).toString());
                pattern.id = context.getUniqueId("pattern");
                pattern.append(image);
                box.before(pattern);
                box.setAttribute("fill", `url(#${pattern.id})`);
              }
            } else if (/^(-webkit-)?linear-gradient$/.test(backgroundNode.value)) {
              const linearGradientCss = import_postcss_value_parser2.default.stringify(backgroundNode);
              const svgLinearGradient = convertLinearGradient(linearGradientCss, context);
              if (backgroundPositionX !== 0 || backgroundPositionY !== 0) {
                svgLinearGradient.setAttribute("gradientTransform", `translate(${backgroundPositionX}, ${backgroundPositionY})`);
              }
              svgLinearGradient.id = context.getUniqueId("linear-gradient");
              box.before(svgLinearGradient);
              box.setAttribute("fill", `url(#${svgLinearGradient.id})`);
            }
          }
        }
      }
      if (!hasUniformBorder(styles)) {
        for (const borderLine of createBorders(styles, bounds, context)) {
          backgroundAndBordersContainer.append(borderLine);
        }
      }
    }
  }
  function createBox(bounds, context) {
    const box = context.svgDocument.createElementNS(svgNamespace, "rect");
    box.setAttribute("width", bounds.width.toString());
    box.setAttribute("height", bounds.height.toString());
    box.setAttribute("x", bounds.x.toString());
    box.setAttribute("y", bounds.y.toString());
    return box;
  }
  function createBackgroundAndBorderBox(bounds, styles, context) {
    const background = createBox(bounds, context);
    if (styles.backgroundColor) {
      background.setAttribute("fill", styles.backgroundColor);
    }
    if (hasUniformBorder(styles)) {
      background.setAttribute("stroke", styles.borderTopColor);
      background.setAttribute("stroke-width", styles.borderTopWidth);
      if (styles.borderTopStyle === "dashed") {
        background.setAttribute("stroke-dasharray", "1");
      }
    }
    const overlappingCurvesFactor = calculateOverlappingCurvesFactor(styles, bounds);
    const radiusX = getBorderRadiiForSide("top", styles, bounds)[0] * overlappingCurvesFactor;
    const radiusY = getBorderRadiiForSide("left", styles, bounds)[0] * overlappingCurvesFactor;
    if (radiusX !== 0) {
      background.setAttribute("rx", radiusX.toString());
    }
    if (radiusY !== 0) {
      background.setAttribute("ry", radiusY.toString());
    }
    return background;
  }
  function* createBorders(styles, bounds, context) {
    for (const side of ["top", "bottom", "right", "left"]) {
      if (hasBorder(styles, side)) {
        yield createBorder(styles, bounds, side, context);
      }
    }
  }
  function hasBorder(styles, side) {
    return !!styles.getPropertyValue(`border-${side}-color`) && !isTransparent(styles.getPropertyValue(`border-${side}-color`)) && styles.getPropertyValue(`border-${side}-width`) !== "0px";
  }
  function createBorder(styles, bounds, side, context) {
    const border = context.svgDocument.createElementNS(svgNamespace, "line");
    border.setAttribute("stroke-linecap", "square");
    const color = styles.getPropertyValue(`border-${side}-color`);
    border.setAttribute("stroke", color);
    border.setAttribute("stroke-width", styles.getPropertyValue(`border-${side}-width`));
    const borderStyle = styles.getPropertyValue(`border-${side}-style`);
    if (borderStyle === "inset" && (side === "top" || side === "left") || borderStyle === "outset" && (side === "right" || side === "bottom")) {
      const match = color.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/);
      if (!match) {
        throw new Error(`Unexpected color: ${color}`);
      }
      const components = match.slice(1, 4).map((value) => parseInt(value, 10) * 0.3);
      if (match[4]) {
        components.push(parseFloat(match[4]));
      }
      border.setAttribute("stroke", `rgba(${components.join(", ")})`);
    }
    if (side === "top") {
      border.setAttribute("x1", bounds.left.toString());
      border.setAttribute("x2", bounds.right.toString());
      border.setAttribute("y1", bounds.top.toString());
      border.setAttribute("y2", bounds.top.toString());
    } else if (side === "left") {
      border.setAttribute("x1", bounds.left.toString());
      border.setAttribute("x2", bounds.left.toString());
      border.setAttribute("y1", bounds.top.toString());
      border.setAttribute("y2", bounds.bottom.toString());
    } else if (side === "right") {
      border.setAttribute("x1", bounds.right.toString());
      border.setAttribute("x2", bounds.right.toString());
      border.setAttribute("y1", bounds.top.toString());
      border.setAttribute("y2", bounds.bottom.toString());
    } else if (side === "bottom") {
      border.setAttribute("x1", bounds.left.toString());
      border.setAttribute("x2", bounds.right.toString());
      border.setAttribute("y1", bounds.bottom.toString());
      border.setAttribute("y2", bounds.bottom.toString());
    }
    return border;
  }
  function createSvgAnchor(element, context) {
    const svgAnchor = context.svgDocument.createElementNS(svgNamespace, "a");
    if (element.href && !element.href.startsWith("javascript:")) {
      svgAnchor.setAttribute("href", element.href);
    }
    if (element.rel) {
      svgAnchor.setAttribute("rel", element.rel);
    }
    if (element.target) {
      svgAnchor.setAttribute("target", element.target);
    }
    if (element.download) {
      svgAnchor.setAttribute("download", element.download);
    }
    return svgAnchor;
  }

  // node_modules/dom-to-svg/lib/traversal.js
  function walkNode(node, context) {
    if (isElement(node)) {
      handleElement(node, context);
    } else if (isTextNode(node)) {
      handleTextNode(node, context);
    }
  }

  // node_modules/dom-to-svg/lib/inline.js
  var import_postcss_value_parser3 = __toESM(require_lib(), 1);
  async function inlineResources(element) {
    await Promise.all([
      ...[...element.children].map(inlineResources),
      (async () => {
        var _a;
        if (isSVGImageElement(element)) {
          const blob = await withTimeout(1e4, `Timeout fetching ${element.href.baseVal}`, () => fetchResource(element.href.baseVal));
          if (blob.type === "image/svg+xml") {
            assert(element.ownerDocument, "Expected <image> element to have ownerDocument");
            const embeddedSvgDocument = new DOMParser().parseFromString(await blob.text(), "image/svg+xml");
            const svgRoot = embeddedSvgDocument.documentElement;
            svgRoot.setAttribute("x", element.getAttribute("x"));
            svgRoot.setAttribute("y", element.getAttribute("y"));
            svgRoot.setAttribute("width", element.getAttribute("width"));
            svgRoot.setAttribute("height", element.getAttribute("height"));
            svgRoot.remove();
            element.replaceWith(svgRoot);
            try {
              const svgDocument = element.ownerDocument;
              const mount = svgDocument.createElementNS(svgNamespace, "g");
              assert(element.id, "<image> element must have ID");
              handleSvgNode(svgRoot, {
                currentSvgParent: mount,
                svgDocument,
                idPrefix: `${element.id}-`,
                options: {
                  // SVGs embedded through <img> are never interactive.
                  keepLinks: false,
                  captureArea: svgRoot.viewBox.baseVal
                }
              });
              mount.dataset.tag = "img";
              mount.setAttribute("role", "img");
              svgRoot.replaceWith(mount);
            } finally {
              svgRoot.remove();
            }
          } else {
            const dataUrl = await blobToDataURL(blob);
            element.dataset.src = element.href.baseVal;
            element.setAttribute("xlink:href", dataUrl.href);
          }
        } else if (isSVGStyleElement(element)) {
          try {
            const promises = [];
            const parsedSheet = parse((_a = element.textContent) !== null && _a !== void 0 ? _a : "");
            parsedSheet.walkAtRules("font-face", (fontFaceRule) => {
              fontFaceRule.walkDecls("src", (sourceDeclaration) => {
                const parsedSourceValue = (0, import_postcss_value_parser3.default)(sourceDeclaration.value);
                parsedSourceValue.walk((node) => {
                  if (node.type === "function" && node.value === "url" && node.nodes[0]) {
                    const urlArgumentNode = node.nodes[0];
                    if (urlArgumentNode.type === "string" || urlArgumentNode.type === "word") {
                      promises.push(inlineCssFontUrlArgumentNode(urlArgumentNode));
                    }
                  }
                });
                sourceDeclaration.value = import_postcss_value_parser3.default.stringify(parsedSourceValue.nodes);
              });
            });
            await Promise.all(promises);
            element.textContent = parsedSheet.toString();
          } catch (error) {
            console.error("Error inlining stylesheet", element.sheet, error);
          }
        }
      })().catch((error) => {
        console.error("Error inlining resource for element", element, error);
      })
    ]);
  }
  async function inlineCssFontUrlArgumentNode(urlArgumentNode) {
    try {
      const url = new URL(unescapeStringValue(urlArgumentNode.value));
      const blob = await withTimeout(1e4, `Timeout fetching ${url.href}`, () => fetchResource(url.href));
      if (!blob.type.startsWith("font/") && !blob.type.startsWith("application/font-") && !blob.type.startsWith("application/x-font-") && !blob.type.startsWith("image/svg+xml") && !blob.type.startsWith("application/vnd.ms-fontobject")) {
        throw new Error(`Invalid response MIME type inlining font at ${url.href}: Expected font MIME type, got ${blob.type}`);
      }
      const dataUrl = await blobToDataURL(blob);
      urlArgumentNode.value = dataUrl.href;
    } catch (error) {
      console.error(`Error inlining ${urlArgumentNode.value}`, error);
    }
  }
  async function fetchResource(url) {
    assert(url, "No URL passed");
    const headers = new Headers();
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const blob = await response.blob();
    return blob;
  }
  async function blobToDataURL(blob) {
    const reader = new FileReader();
    await new Promise((resolve, reject) => {
      reader.addEventListener("error", () => reject(new Error("Error loading resource with FileLoader")));
      reader.addEventListener("load", () => resolve());
      reader.readAsDataURL(blob);
    });
    return new URL(reader.result);
  }

  // node_modules/dom-to-svg/lib/index.js
  function documentToSVG(document3, options) {
    return elementToSVG(document3.documentElement, options);
  }
  function elementToSVG(element, options) {
    var _a, _b, _c, _d;
    const svgDocument = element.ownerDocument.implementation.createDocument(svgNamespace, "svg", null);
    const svgElement = svgDocument.documentElement;
    svgElement.setAttribute("xmlns", svgNamespace);
    svgElement.setAttribute("xmlns:xlink", xlinkNamespace);
    svgElement.append(svgDocument.createComment(
      // "--" is invalid in comments, percent-encode.
      ` Generated by dom-to-svg from ${element.ownerDocument.location.href.replace(/--/g, "%2D%2D")} `
    ));
    const styleElement = svgDocument.createElementNS(svgNamespace, "style");
    for (const styleSheet of element.ownerDocument.styleSheets) {
      try {
        for (const rule2 of (_a = styleSheet.rules) !== null && _a !== void 0 ? _a : []) {
          if (!isCSSFontFaceRule(rule2)) {
            continue;
          }
          const styleSheetHref = (_b = rule2.parentStyleSheet) === null || _b === void 0 ? void 0 : _b.href;
          if (styleSheetHref) {
            const parsedSourceValue = (0, import_postcss_value_parser4.default)(rule2.style.getPropertyValue("src"));
            parsedSourceValue.walk((node) => {
              if (node.type === "function" && node.value === "url" && node.nodes[0]) {
                const urlArgumentNode = node.nodes[0];
                if (urlArgumentNode.type === "string" || urlArgumentNode.type === "word") {
                  urlArgumentNode.value = new URL(unescapeStringValue(urlArgumentNode.value), styleSheetHref).href;
                }
              }
            });
            const updatedFontFaceRule = parse(rule2.cssText);
            updatedFontFaceRule.walkDecls("src", (declaration) => {
              declaration.value = import_postcss_value_parser4.default.stringify(parsedSourceValue.nodes);
            });
            styleElement.append(updatedFontFaceRule.toString() + "\n");
          }
        }
      } catch (error) {
        console.error("Error resolving @font-face src URLs for styleSheet, skipping", styleSheet, error);
      }
    }
    svgElement.append(styleElement);
    walkNode(element, {
      svgDocument,
      currentSvgParent: svgElement,
      stackingLayers: createStackingLayers(svgElement),
      parentStackingLayer: svgElement,
      getUniqueId: createIdGenerator(),
      labels: /* @__PURE__ */ new Map(),
      ancestorMasks: [],
      options: {
        captureArea: (_c = options === null || options === void 0 ? void 0 : options.captureArea) !== null && _c !== void 0 ? _c : element.getBoundingClientRect(),
        keepLinks: (options === null || options === void 0 ? void 0 : options.keepLinks) !== false
      }
    });
    const bounds = (_d = options === null || options === void 0 ? void 0 : options.captureArea) !== null && _d !== void 0 ? _d : element.getBoundingClientRect();
    svgElement.setAttribute("width", bounds.width.toString());
    svgElement.setAttribute("height", bounds.height.toString());
    svgElement.setAttribute("viewBox", `${bounds.x} ${bounds.y} ${bounds.width} ${bounds.height}`);
    return svgDocument;
  }

  // scripts/dom-to-svg-runner.js
  window.capturePageToVectorSvg = async function() {
    const appShell = document.getElementById("app-shell-capture-root");
    const target = appShell || document.documentElement;
    const captureArea = target.getBoundingClientRect();
    const svgDoc = appShell ? elementToSVG(appShell, { captureArea: new DOMRect(0, 0, window.innerWidth, window.innerHeight) }) : documentToSVG(document, { captureArea: new DOMRect(0, 0, document.documentElement.scrollWidth, document.documentElement.scrollHeight) });
    const root2 = svgDoc.documentElement;
    document.body.prepend(root2);
    try {
      await inlineResources(root2);
    } finally {
      root2.remove();
    }
    return new XMLSerializer().serializeToString(root2);
  };
})();
