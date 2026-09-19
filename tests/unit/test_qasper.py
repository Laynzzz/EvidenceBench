def test_partial_paragraph_requires_all_supporting_pages():
    from evidencebench.qasper import locate_paragraph, locate_span

    start = (
        "The model was trained using a large collection of documents "
        "and evaluated on several tasks."
    )
    end = "The optimizer was Adafactor."
    assert locate_paragraph(start + " " + end, [start, end]) is None
    assert locate_span(start + " " + end, [start, end]) == (1, 2)
    assert locate_span(start + " " + end, [start, "An unrelated appendix."]) is None


def test_mapping_handles_pdf_joined_words_and_reference_placeholders():
    from evidencebench.qasper import locate_span

    paragraph = (
        "Our classifier uses contextual word vectors BIBREF2 and a linear classification head."
    )
    pdf = "Ourclassifierusescontextualwordvectors (Smith, 2020) andalinearclassi-\nficationhead."
    assert locate_span(paragraph, [pdf]) == (1, 1)


def test_alignment_does_not_conflate_decimal_numbers():
    from evidencebench.qasper import locate_span

    text = "The model reduced the overall error rate by 1.0 percent on the evaluation set."
    assert locate_span(text, [text.replace("1.0", "10")]) is None


def test_page_alignment_rejects_ambiguous_or_missing_evidence():
    from evidencebench.qasper import locate_paragraph

    evidence = "Our classifier uses contextual word vectors and a linear classification head."
    assert locate_paragraph(evidence, ["Unrelated cover sheet", evidence]) == 2
    assert locate_paragraph(evidence, [evidence, evidence]) is None
    assert locate_paragraph(evidence, ["This unrelated paper has no results."]) is None


def test_human_answer_import_rejects_disagreement_and_visual_evidence():
    from evidencebench.qasper import select_annotation

    answer = dict(
        unanswerable=False,
        evidence=["The model uses twelve layers."],
        extractive_spans=["twelve"],
        free_form_answer="",
        yes_no=None,
    )
    assert select_annotation({"answers": [{"answer": answer}]})["criteria"] == "twelve"
    assert (
        select_annotation(
            {"answers": [{"answer": answer}, {"answer": dict(answer, unanswerable=True)}]}
        )
        is None
    )
    assert (
        select_annotation(
            {"answers": [{"answer": dict(answer, evidence=["FLOAT SELECTED: table 1"])}]}
        )
        is None
    )


def test_false_boolean_answer_is_not_discarded():
    from evidencebench.qasper import select_annotation

    answer = dict(
        unanswerable=False,
        evidence=["No pretraining was used."],
        extractive_spans=[],
        free_form_answer="",
        yes_no=False,
    )
    assert select_annotation({"answers": [{"answer": answer}]})["criteria"] == "No"
