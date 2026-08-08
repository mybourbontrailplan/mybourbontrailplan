/*!
 * qr.js - minimal QR Code encoder (byte mode) for mybourbontrailplan.com
 *
 * Vendored deliberately rather than calling a third-party QR image API: an
 * external endpoint would leak the URL, add a dependency we do not control, and
 * can rot silently on printed material that lives in a guest binder for years.
 *
 * Implements ISO/IEC 18004 byte mode, versions 1-40, EC levels L/M/Q/H, with
 * automatic version selection and mask scoring. The Reed-Solomon block table
 * and alignment-pattern coordinates below were generated from the `qrcode`
 * Python package already used by scripts/generate_pdf_map.py, and the encoder
 * output is verified module-for-module against that same library for every
 * version, level, and mask by scripts/verify_qr.js (2672 matrices, 0 diffs).
 * Mask *selection* can differ from that library by design; see the verifier
 * header. Mask choice is a scannability heuristic, never a decodability issue.
 *
 * MIT licensed.
 */
(function (root) {
  'use strict';

  var RS_TABLE=[[[1,26,19],[1,26,16],[1,26,13],[1,26,9]],[[1,44,34],[1,44,28],[1,44,22],[1,44,16]],[[1,70,55],[1,70,44],[2,35,17],[2,35,13]],[[1,100,80],[2,50,32],[2,50,24],[4,25,9]],[[1,134,108],[2,67,43],[2,33,15,2,34,16],[2,33,11,2,34,12]],[[2,86,68],[4,43,27],[4,43,19],[4,43,15]],[[2,98,78],[4,49,31],[2,32,14,4,33,15],[4,39,13,1,40,14]],[[2,121,97],[2,60,38,2,61,39],[4,40,18,2,41,19],[4,40,14,2,41,15]],[[2,146,116],[3,58,36,2,59,37],[4,36,16,4,37,17],[4,36,12,4,37,13]],[[2,86,68,2,87,69],[4,69,43,1,70,44],[6,43,19,2,44,20],[6,43,15,2,44,16]],[[4,101,81],[1,80,50,4,81,51],[4,50,22,4,51,23],[3,36,12,8,37,13]],[[2,116,92,2,117,93],[6,58,36,2,59,37],[4,46,20,6,47,21],[7,42,14,4,43,15]],[[4,133,107],[8,59,37,1,60,38],[8,44,20,4,45,21],[12,33,11,4,34,12]],[[3,145,115,1,146,116],[4,64,40,5,65,41],[11,36,16,5,37,17],[11,36,12,5,37,13]],[[5,109,87,1,110,88],[5,65,41,5,66,42],[5,54,24,7,55,25],[11,36,12,7,37,13]],[[5,122,98,1,123,99],[7,73,45,3,74,46],[15,43,19,2,44,20],[3,45,15,13,46,16]],[[1,135,107,5,136,108],[10,74,46,1,75,47],[1,50,22,15,51,23],[2,42,14,17,43,15]],[[5,150,120,1,151,121],[9,69,43,4,70,44],[17,50,22,1,51,23],[2,42,14,19,43,15]],[[3,141,113,4,142,114],[3,70,44,11,71,45],[17,47,21,4,48,22],[9,39,13,16,40,14]],[[3,135,107,5,136,108],[3,67,41,13,68,42],[15,54,24,5,55,25],[15,43,15,10,44,16]],[[4,144,116,4,145,117],[17,68,42],[17,50,22,6,51,23],[19,46,16,6,47,17]],[[2,139,111,7,140,112],[17,74,46],[7,54,24,16,55,25],[34,37,13]],[[4,151,121,5,152,122],[4,75,47,14,76,48],[11,54,24,14,55,25],[16,45,15,14,46,16]],[[6,147,117,4,148,118],[6,73,45,14,74,46],[11,54,24,16,55,25],[30,46,16,2,47,17]],[[8,132,106,4,133,107],[8,75,47,13,76,48],[7,54,24,22,55,25],[22,45,15,13,46,16]],[[10,142,114,2,143,115],[19,74,46,4,75,47],[28,50,22,6,51,23],[33,46,16,4,47,17]],[[8,152,122,4,153,123],[22,73,45,3,74,46],[8,53,23,26,54,24],[12,45,15,28,46,16]],[[3,147,117,10,148,118],[3,73,45,23,74,46],[4,54,24,31,55,25],[11,45,15,31,46,16]],[[7,146,116,7,147,117],[21,73,45,7,74,46],[1,53,23,37,54,24],[19,45,15,26,46,16]],[[5,145,115,10,146,116],[19,75,47,10,76,48],[15,54,24,25,55,25],[23,45,15,25,46,16]],[[13,145,115,3,146,116],[2,74,46,29,75,47],[42,54,24,1,55,25],[23,45,15,28,46,16]],[[17,145,115],[10,74,46,23,75,47],[10,54,24,35,55,25],[19,45,15,35,46,16]],[[17,145,115,1,146,116],[14,74,46,21,75,47],[29,54,24,19,55,25],[11,45,15,46,46,16]],[[13,145,115,6,146,116],[14,74,46,23,75,47],[44,54,24,7,55,25],[59,46,16,1,47,17]],[[12,151,121,7,152,122],[12,75,47,26,76,48],[39,54,24,14,55,25],[22,45,15,41,46,16]],[[6,151,121,14,152,122],[6,75,47,34,76,48],[46,54,24,10,55,25],[2,45,15,64,46,16]],[[17,152,122,4,153,123],[29,74,46,14,75,47],[49,54,24,10,55,25],[24,45,15,46,46,16]],[[4,152,122,18,153,123],[13,74,46,32,75,47],[48,54,24,14,55,25],[42,45,15,32,46,16]],[[20,147,117,4,148,118],[40,75,47,7,76,48],[43,54,24,22,55,25],[10,45,15,67,46,16]],[[19,148,118,6,149,119],[18,75,47,31,76,48],[34,54,24,34,55,25],[20,45,15,61,46,16]]];
  var ALIGN=[[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],[6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],[6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],[6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],[6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,114,142],[6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,80,106,132,158],[6,32,58,84,110,136,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]];

  var ECL = { L: 0, M: 1, Q: 2, H: 3 };
  /* Format-info bit patterns per level, in spec order (not our array order). */
  var ECL_FORMAT_BITS = { L: 1, M: 0, Q: 3, H: 2 };

  /* ---------- GF(256) arithmetic, primitive polynomial 0x11d ---------- */
  var EXP = new Uint8Array(512), LOG = new Uint8Array(256);
  (function () {
    var x = 1, i;
    for (i = 0; i < 255; i++) {
      EXP[i] = x; LOG[x] = i;
      x <<= 1;
      if (x & 0x100) x ^= 0x11d;
    }
    for (i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
  })();

  function gmul(a, b) {
    if (a === 0 || b === 0) return 0;
    return EXP[LOG[a] + LOG[b]];
  }

  /* Generator polynomial for n EC codewords: product of (x - a^i). */
  function rsGenerator(n) {
    var poly = [1], i, j;
    for (i = 0; i < n; i++) {
      var next = new Array(poly.length + 1);
      for (j = 0; j < next.length; j++) next[j] = 0;
      for (j = 0; j < poly.length; j++) {
        next[j] ^= poly[j];
        next[j + 1] ^= gmul(poly[j], EXP[i]);
      }
      poly = next;
    }
    return poly;
  }

  function rsEncode(data, ecCount) {
    var gen = rsGenerator(ecCount), res = [], i, j;
    for (i = 0; i < ecCount; i++) res.push(0);
    for (i = 0; i < data.length; i++) {
      var factor = data[i] ^ res[0];
      res.shift();
      res.push(0);
      for (j = 0; j < ecCount; j++) res[j] ^= gmul(gen[j + 1], factor);
    }
    return res;
  }

  /* ---------- bit buffer ---------- */
  function BitBuf() { this.bits = []; }
  BitBuf.prototype.put = function (val, len) {
    for (var i = len - 1; i >= 0; i--) this.bits.push((val >>> i) & 1);
  };

  /* ---------- capacity helpers ---------- */
  function blocksFor(version, ecl) {
    var raw = RS_TABLE[version - 1][ECL[ecl]], out = [], i, c;
    for (i = 0; i < raw.length; i += 3) {
      for (c = 0; c < raw[i]; c++) out.push({ total: raw[i + 1], data: raw[i + 2] });
    }
    return out;
  }
  function dataCodewords(version, ecl) {
    var b = blocksFor(version, ecl), s = 0;
    for (var i = 0; i < b.length; i++) s += b[i].data;
    return s;
  }
  function charCountBits(version) { return version < 10 ? 8 : 16; }

  function utf8Bytes(str) {
    var out = [], enc = encodeURIComponent(str), i;
    for (i = 0; i < enc.length; i++) {
      if (enc[i] === '%') { out.push(parseInt(enc.substr(i + 1, 2), 16)); i += 2; }
      else out.push(enc.charCodeAt(i));
    }
    return out;
  }

  /* Byte-mode payload capacity of a given version and level. */
  function capacityBytes(version, ecl) {
    return Math.floor((dataCodewords(version, ecl) * 8 - 4 - charCountBits(version)) / 8);
  }

  function pickVersion(byteLen, ecl, minV, maxV) {
    for (var v = minV; v <= maxV; v++) {
      if (byteLen <= capacityBytes(v, ecl)) return v;
    }
    return -1;
  }

  /* ---------- codeword stream ---------- */
  function buildCodewords(bytes, version, ecl) {
    var bb = new BitBuf(), i, j;
    bb.put(4, 4);                            /* byte mode */
    bb.put(bytes.length, charCountBits(version));
    for (i = 0; i < bytes.length; i++) bb.put(bytes[i], 8);

    var capBits = dataCodewords(version, ecl) * 8;
    bb.put(0, Math.min(4, capBits - bb.bits.length));
    while (bb.bits.length % 8 !== 0) bb.bits.push(0);

    var data = [];
    for (i = 0; i < bb.bits.length; i += 8) {
      var b = 0;
      for (j = 0; j < 8; j++) b = (b << 1) | bb.bits[i + j];
      data.push(b);
    }
    var pad = [0xEC, 0x11], p = 0;
    while (data.length < capBits / 8) data.push(pad[p++ % 2]);

    /* split into blocks, compute EC, then interleave both halves */
    var blocks = blocksFor(version, ecl), pos = 0, dataBlocks = [], ecBlocks = [];
    for (i = 0; i < blocks.length; i++) {
      var d = data.slice(pos, pos + blocks[i].data);
      pos += blocks[i].data;
      dataBlocks.push(d);
      ecBlocks.push(rsEncode(d, blocks[i].total - blocks[i].data));
    }
    var out = [], maxD = 0, maxE = 0;
    for (i = 0; i < dataBlocks.length; i++) if (dataBlocks[i].length > maxD) maxD = dataBlocks[i].length;
    for (i = 0; i < ecBlocks.length; i++) if (ecBlocks[i].length > maxE) maxE = ecBlocks[i].length;
    for (i = 0; i < maxD; i++) {
      for (j = 0; j < dataBlocks.length; j++) if (i < dataBlocks[j].length) out.push(dataBlocks[j][i]);
    }
    for (i = 0; i < maxE; i++) {
      for (j = 0; j < ecBlocks.length; j++) if (i < ecBlocks[j].length) out.push(ecBlocks[j][i]);
    }
    return out;
  }

  /* ---------- matrix ---------- */
  function newGrid(size) {
    var g = [], i, j;
    for (i = 0; i < size; i++) {
      var row = new Int8Array(size);
      for (j = 0; j < size; j++) row[j] = -1;
      g.push(row);
    }
    return g;
  }

  function placeFinder(g, r, c) {
    for (var dr = -1; dr <= 7; dr++) {
      for (var dc = -1; dc <= 7; dc++) {
        var rr = r + dr, cc = c + dc;
        if (rr < 0 || cc < 0 || rr >= g.length || cc >= g.length) continue;
        var inRing = (dr >= 0 && dr <= 6 && dc >= 0 && dc <= 6) &&
          (dr === 0 || dr === 6 || dc === 0 || dc === 6 || (dr >= 2 && dr <= 4 && dc >= 2 && dc <= 4));
        g[rr][cc] = inRing ? 1 : 0;
      }
    }
  }

  function placeFunctionPatterns(g, version) {
    var size = g.length, i, k;
    placeFinder(g, 0, 0);
    placeFinder(g, 0, size - 7);
    placeFinder(g, size - 7, 0);

    for (i = 8; i < size - 8; i++) {           /* timing patterns */
      var v = (i % 2 === 0) ? 1 : 0;
      g[6][i] = v; g[i][6] = v;
    }

    var pos = ALIGN[version - 1];              /* alignment patterns */
    for (var a = 0; a < pos.length; a++) {
      for (var b = 0; b < pos.length; b++) {
        var r = pos[a], c = pos[b];
        if ((r === 6 && c === 6) || (r === 6 && c === size - 7) || (r === size - 7 && c === 6)) continue;
        for (var dr = -2; dr <= 2; dr++) {
          for (var dc = -2; dc <= 2; dc++) {
            var ring = Math.max(Math.abs(dr), Math.abs(dc));
            g[r + dr][c + dc] = (ring === 1) ? 0 : 1;
          }
        }
      }
    }

    for (i = 0; i <= 8; i++) {                 /* reserve format areas */
      if (g[8][i] === -1) g[8][i] = 0;
      if (g[i][8] === -1) g[i][8] = 0;
    }
    for (i = 0; i < 8; i++) {
      if (g[8][size - 1 - i] === -1) g[8][size - 1 - i] = 0;
      if (g[size - 1 - i][8] === -1) g[size - 1 - i][8] = 0;
    }
    g[size - 8][8] = 1;                        /* dark module */

    if (version >= 7) {                        /* reserve version areas */
      for (i = 0; i < 6; i++) {
        for (k = 0; k < 3; k++) {
          if (g[size - 11 + k][i] === -1) g[size - 11 + k][i] = 0;
          if (g[i][size - 11 + k] === -1) g[i][size - 11 + k] = 0;
        }
      }
    }
  }

  /* Which cells are function modules, so data placement skips them. */
  function functionMask(version) {
    var size = 4 * version + 17, g = newGrid(size), m = [], i, j;
    placeFunctionPatterns(g, version);
    for (i = 0; i < size; i++) {
      m.push(new Uint8Array(size));
      for (j = 0; j < size; j++) m[i][j] = g[i][j] === -1 ? 0 : 1;
    }
    return m;
  }

  function placeData(g, fn, codewords) {
    var size = g.length, bitIdx = 0, total = codewords.length * 8;
    for (var right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;              /* skip the vertical timing column */
      for (var vert = 0; vert < size; vert++) {
        for (var j = 0; j < 2; j++) {
          var c = right - j;
          var upward = ((right + 1) & 2) === 0;
          var r = upward ? size - 1 - vert : vert;
          if (fn[r][c]) continue;
          var bit = 0;
          if (bitIdx < total) bit = (codewords[bitIdx >>> 3] >>> (7 - (bitIdx & 7))) & 1;
          g[r][c] = bit;
          bitIdx++;
        }
      }
    }
  }

  var MASKS = [
    function (i, j) { return (i + j) % 2 === 0; },
    function (i) { return i % 2 === 0; },
    function (i, j) { return j % 3 === 0; },
    function (i, j) { return (i + j) % 3 === 0; },
    function (i, j) { return (Math.floor(i / 2) + Math.floor(j / 3)) % 2 === 0; },
    function (i, j) { return (i * j) % 2 + (i * j) % 3 === 0; },
    function (i, j) { return ((i * j) % 2 + (i * j) % 3) % 2 === 0; },
    function (i, j) { return ((i + j) % 2 + (i * j) % 3) % 2 === 0; }
  ];

  function bitLen(n) { var c = 0; while (n !== 0) { c++; n >>>= 1; } return c; }
  function bchFormat(data) {                   /* 15-bit, G15 = 0x537 */
    var d = data << 10;
    while (bitLen(d) - 11 >= 0) d ^= 0x537 << (bitLen(d) - 11);
    return ((data << 10) | d) ^ 0x5412;
  }
  function bchVersion(data) {                  /* 18-bit, G18 = 0x1f25 */
    var d = data << 12;
    while (bitLen(d) - 13 >= 0) d ^= 0x1f25 << (bitLen(d) - 13);
    return (data << 12) | d;
  }

  /* Format-info placement, mirroring qrcode's setup_type_info exactly.
     Bit 0 starts at (0,8) and runs DOWN column 8; the mirrored copy runs along
     row 8 from the right edge. Writing bit 0 at (8,0) instead, running along
     row 8, is the transpose of this and produces a matrix that looks plausible
     and does not decode. */
  function writeFormat(g, ecl, mask) {
    var size = g.length, bits = bchFormat((ECL_FORMAT_BITS[ecl] << 3) | mask), i, bit;
    for (i = 0; i < 15; i++) {                 /* vertical, column 8 */
      bit = (bits >> i) & 1;
      if (i < 6) g[i][8] = bit;
      else if (i < 8) g[i + 1][8] = bit;
      else g[size - 15 + i][8] = bit;
    }
    for (i = 0; i < 15; i++) {                 /* horizontal, row 8 */
      bit = (bits >> i) & 1;
      if (i < 8) g[8][size - i - 1] = bit;
      else if (i < 9) g[8][15 - i] = bit;
      else g[8][14 - i] = bit;
    }
    g[size - 8][8] = 1;                        /* dark module, always set last */
  }

  function writeVersion(g, version) {
    if (version < 7) return;
    var size = g.length, bits = bchVersion(version);
    for (var i = 0; i < 18; i++) {
      var b = (bits >> i) & 1, a = Math.floor(i / 3), bb = i % 3;
      g[size - 11 + bb][a] = b;
      g[a][size - 11 + bb] = b;
    }
  }

  function penalty(g) {
    var size = g.length, score = 0, i, j, run, last;
    /* N1: runs of 5 or more */
    for (i = 0; i < size; i++) {
      run = 1; last = g[i][0];
      for (j = 1; j < size; j++) {
        if (g[i][j] === last) run++;
        else { if (run >= 5) score += 3 + (run - 5); run = 1; last = g[i][j]; }
      }
      if (run >= 5) score += 3 + (run - 5);
      run = 1; last = g[0][i];
      for (j = 1; j < size; j++) {
        if (g[j][i] === last) run++;
        else { if (run >= 5) score += 3 + (run - 5); run = 1; last = g[j][i]; }
      }
      if (run >= 5) score += 3 + (run - 5);
    }
    /* N2: 2x2 blocks of one colour */
    for (i = 0; i < size - 1; i++) {
      for (j = 0; j < size - 1; j++) {
        var v = g[i][j];
        if (v === g[i][j + 1] && v === g[i + 1][j] && v === g[i + 1][j + 1]) score += 3;
      }
    }
    /* N3: 1:1:3:1:1 finder-like pattern preceded or followed by a light area 4
       modules wide. The 4 light modules must be inside the symbol: off-symbol is
       not a light area, so a pattern flush against the edge does not count.
       Treating out-of-bounds as light over-counts and picks worse masks. */
    var pat = [1, 0, 1, 1, 1, 0, 1];
    function hasPat(get, at) {
      var k, m;
      for (k = 0; k < 7; k++) if (get(at + k) !== pat[k]) return false;
      var beforeOk = true, afterOk = true;
      for (m = 1; m <= 4; m++) if (get(at - m) !== 0) { beforeOk = false; break; }
      for (m = 0; m < 4; m++) if (get(at + 7 + m) !== 0) { afterOk = false; break; }
      return beforeOk || afterOk;
    }
    for (i = 0; i < size; i++) {
      for (j = 0; j <= size - 7; j++) {
        var row = i;
        var getR = function (k) { return (k < 0 || k >= size) ? null : g[row][k]; };
        var getC = function (k) { return (k < 0 || k >= size) ? null : g[k][row]; };
        if (hasPat(getR, j)) score += 40;
        if (hasPat(getC, j)) score += 40;
      }
    }
    /* N4: deviation from a 50% dark ratio */
    var dark = 0;
    for (i = 0; i < size; i++) for (j = 0; j < size; j++) dark += g[i][j];
    score += Math.floor(Math.abs(dark * 100 / (size * size) - 50) / 5) * 10;
    return score;
  }

  function encode(text, opts) {
    opts = opts || {};
    var ecl = opts.ecl || 'M';
    if (!(ecl in ECL)) throw new Error('bad ecl: ' + ecl);
    var bytes = utf8Bytes(String(text));
    var version = opts.version ||
      pickVersion(bytes.length, ecl, opts.minVersion || 1, opts.maxVersion || 40);
    if (version < 1) throw new Error('data too long for a QR code at level ' + ecl);
    /* An explicitly requested version still has to fit the data. Without this
       check buildCodewords silently overruns the codeword budget and emits a
       matrix that looks fine and does not decode. */
    if (bytes.length > capacityBytes(version, ecl)) {
      throw new Error('data too long for version ' + version + ' at level ' + ecl +
        ' (' + bytes.length + ' > ' + capacityBytes(version, ecl) + ' bytes)');
    }

    var codewords = buildCodewords(bytes, version, ecl);
    var size = 4 * version + 17;
    var fn = functionMask(version);
    var masks = (opts.mask === undefined || opts.mask === null) ? [0, 1, 2, 3, 4, 5, 6, 7] : [opts.mask];
    var best = null, mi, r, c;

    for (mi = 0; mi < masks.length; mi++) {
      var m = masks[mi];
      var g = newGrid(size);
      placeFunctionPatterns(g, version);
      placeData(g, fn, codewords);
      for (r = 0; r < size; r++) {
        for (c = 0; c < size; c++) {
          if (!fn[r][c] && MASKS[m](r, c)) g[r][c] ^= 1;
        }
      }
      writeFormat(g, ecl, m);
      writeVersion(g, version);
      var s = penalty(g);
      if (!best || s < best.score) best = { score: s, grid: g, mask: m };
    }
    return { size: size, version: version, ecl: ecl, mask: best.mask, modules: best.grid };
  }

  /* ---------- renderers ---------- */
  function toCanvas(qr, canvas, opts) {
    opts = opts || {};
    var quiet = opts.quiet === undefined ? 4 : opts.quiet;   /* spec minimum */
    var total = qr.size + quiet * 2;
    /* Round the module scale UP so the bitmap always meets or exceeds the
       requested size. Flooring can land well under it (a 49-module symbol at a
       1024 target floors to 969px), and these get printed. */
    var scale = Math.max(1, Math.ceil((opts.size || 1024) / total));
    var px = total * scale;
    canvas.width = px; canvas.height = px;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = opts.light || '#ffffff';
    ctx.fillRect(0, 0, px, px);
    ctx.fillStyle = opts.dark || '#0E2F44';
    for (var r = 0; r < qr.size; r++) {
      for (var c = 0; c < qr.size; c++) {
        if (qr.modules[r][c]) ctx.fillRect((c + quiet) * scale, (r + quiet) * scale, scale, scale);
      }
    }
    return canvas;
  }

  function toSVG(qr, opts) {
    opts = opts || {};
    var quiet = opts.quiet === undefined ? 4 : opts.quiet;
    var total = qr.size + quiet * 2, d = '', r, c;
    for (r = 0; r < qr.size; r++) {
      for (c = 0; c < qr.size; c++) {
        if (qr.modules[r][c]) d += 'M' + (c + quiet) + ' ' + (r + quiet) + 'h1v1h-1z';
      }
    }
    return '<?xml version="1.0" encoding="UTF-8"?>\n'
      + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + total + ' ' + total + '" '
      + 'width="' + (total * 8) + '" height="' + (total * 8) + '" shape-rendering="crispEdges">'
      + '<rect width="' + total + '" height="' + total + '" fill="' + (opts.light || '#ffffff') + '"/>'
      + '<path d="' + d + '" fill="' + (opts.dark || '#0E2F44') + '"/></svg>';
  }

  root.QR = {
    encode: encode,
    toCanvas: toCanvas,
    toSVG: toSVG,
    capacityBytes: capacityBytes
  };
})(typeof window !== 'undefined' ? window : globalThis);
