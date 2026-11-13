from etl.clean import clean_text, content_hash, normalize_whitespace, strip_html


class TestStripHtml:
    def test_removes_tags_and_decodes_entities(self):
        assert strip_html("<b>Python</b> &amp; SQL") == " Python  & SQL"

    def test_block_tags_become_newlines(self):
        out = clean_text("<p>First</p><p>Second</p><ul><li>A</li><li>B</li></ul>")
        assert out == "First\n\nSecond\n\nA\n\nB"

    def test_br_variants(self):
        assert clean_text("one<br>two<br/>three<BR />four") == "one\ntwo\nthree\nfour"

    def test_drops_script_style_and_comments(self):
        raw = "<style>.x{color:red}</style>Hi<!-- tracking --><script>alert(1)</script> there"
        assert clean_text(raw) == "Hi there"

    def test_keeps_plain_text_angle_brackets(self):
        assert clean_text("GPA < 3.0 or > 2 years") == "GPA < 3.0 or > 2 years"

    def test_escaped_markup_is_decoded_not_stripped(self):
        assert clean_text("Use &lt;div&gt; tags") == "Use <div> tags"


class TestNormalizeWhitespace:
    def test_collapses_spaces_and_tabs(self):
        assert normalize_whitespace("a  \t b  c") == "a b c"

    def test_limits_blank_lines(self):
        assert normalize_whitespace("a\n\n\n\n\nb") == "a\n\nb"

    def test_trims_lines_and_ends(self):
        assert normalize_whitespace("  \n  a  \r\n  b  \n ") == "a\nb"

    def test_removes_zero_width_chars(self):
        assert normalize_whitespace("Re​act﻿") == "React"


class TestCleanText:
    def test_none_and_empty(self):
        assert clean_text(None) == ""
        assert clean_text("") == ""
        assert clean_text("<p> </p>") == ""


class TestContentHash:
    def test_is_sha256_hex(self):
        digest = content_hash("Intern", "Acme", "Do things")
        assert len(digest) == 64
        int(digest, 16)

    def test_ignores_case_and_whitespace(self):
        a = content_hash("Software Intern", "Acme", "Build  things.\nShip them.")
        b = content_hash("software  intern", "ACME ", "build things. ship them.")
        assert a == b

    def test_differs_on_any_field(self):
        base = content_hash("Intern", "Acme", "Do things")
        assert content_hash("Intern", "Globex", "Do things") != base
        assert content_hash("Engineer", "Acme", "Do things") != base
        assert content_hash("Intern", "Acme", "Do other things") != base

    def test_field_boundaries_matter(self):
        # Without a separator, these would concatenate to the same string.
        assert content_hash("ab", "c", "d") != content_hash("a", "bc", "d")

    def test_none_company(self):
        assert content_hash("Intern", None, "x") == content_hash("Intern", "", "x")
