# sourcemap

A tool for generating sourcemaps based on input/output files in linear time.

# Example

File `foo.js`:
```javascript
/**
 * @return {string}
 */
function foo() {
    return "foo";
}
```
File `bar.js`:
```javascript
console.log(foo());
```

Say you have a build procedure which concatenates these files and removes comments and spaces, producing `script.js`:
```javascript
function foo(){return "foo";}console.log(foo());
```

The tool will will generate [sourcemap v3](https://docs.google.com/document/d/1U1RGAehQwRypUTovF1KRlpiOFze0b-_2gc6fAH0KY0k/edit):
```bash
lushnikov:~/prog/sourcemap(master)$ python gensm.py foo.js bar.js script.js > script.js.map
lushnikov:~/prog/sourcemap(master)$ cat script.js.map
{"mappings": "AAGA,SAAS,MACL,QAAQ,MCJZ,QAAQ,IAAI", "sourceRoot": "http://localhost:8090", "sources": ["foo.js", "bar.js"], "version": 3, "names": [], "file": "script.js"}

```

**Notes**:
- `sourceRoot` is set to localhost; change it to whatever you want.
- order of input files is crucial. If the script fails to match inputs with output, it fails with exception `Exception: Failed to match generated and source files`
- Algorithm has linear complexity, though the current implementation is not quite fast and produces ~100k of sourcemapping in a second.
