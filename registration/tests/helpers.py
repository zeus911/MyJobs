from bs4 import BeautifulSoup


def assert_email_inlines_styles(test_case, email, selector=None):
    """
    Asserts that styles in style blocks have been properly inlined.

    Inputs:
    :test_case: Instance of TestCase or a subclass; if called from a test,
        pass in ``self``
    :email: Email to be tested; instance of EmailMessage (or possibly others)
    :selector: Element we should be looking for to confirm inlined styles;
        default: a.btn
    """
    if selector is None:
        selector = 'a.btn'

    body = BeautifulSoup(email.body)

    # Styles start out in a <style> block, which is then inlined and removed
    style = body.select('style')
    test_case.assertEqual(len(style), 0)

    anchors = body.select(selector)
    test_case.assertTrue(len(anchors) > 0)
    for anchor in anchors:
        test_case.assertTrue(len(anchor.attrs['style']) > 0)
