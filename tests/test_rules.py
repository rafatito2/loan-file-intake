"""Rule tests on synthetic case L-0412 (Section 2.3). Run from the repo root: python3 -m unittest -v"""
import unittest
from intake.rules import (file_document, compare_names, salary_conflicts,
                   css_missing_months, draft_problems)

OPEN = {"L-0412": "8-888-4412", "L-0398": "4-123-567"}
CHAT = ["L-0412"]          # Ana's chat belongs to one open case
DRAFT = ("Hola Ana, gracias por enviar tus documentos. Para completar tu expediente nos falta:\n"
         "1) la autorización APC firmada;\n"
         "2) una foto nueva de tu cédula, sin flash (en la anterior no se lee el número);\n"
         "3) tu ficha de la CSS completa: faltan los meses de marzo y abril.\n"
         "Puedes enviarlos por este mismo chat.")
ITEMS = ["autorización APC", "foto nueva de tu cédula", "marzo", "abril"]


class Filing(unittest.TestCase):                      # R-4, FR-5, FR-6, S2, S3
    def test_own_documents_filed(self):
        for ced in ["8-888-4412", "8 - 888 - 4412"]:            # W2, W4, W5, W7
            self.assertEqual(file_document(ced, OPEN, CHAT), {"status": "filed", "case": "L-0412"})

    def test_other_person_held_even_from_same_chat(self):       # W6
        r = file_document("8-777-1203", OPEN, CHAT)
        self.assertEqual(r["status"], "held")
        self.assertEqual(r["reason"], "cedula matches no open case")

    def test_unreadable_cedula_held_with_suggestion(self):      # W1
        r = file_document(None, OPEN, CHAT)
        self.assertEqual((r["status"], r["suggestion"]), ("held", "L-0412"))

    def test_no_suggestion_when_chat_ambiguous(self):
        self.assertIsNone(file_document(None, OPEN, ["L-0412", "L-0398"])["suggestion"])


class Names(unittest.TestCase):                       # R-6, FR-8, NFR-7
    def test_married_name_is_variant_not_conflict(self):        # W7
        self.assertEqual(compare_names("Ana Rodríguez", "Ana M. Rodríguez de Pérez"), "variant")

    def test_case_and_accents_match(self):
        self.assertEqual(compare_names("Ana Rodríguez", "ANA RODRIGUEZ"), "match")


class Salary(unittest.TestCase):                      # R-7, FR-9, S5
    VALUES = [("W2", "gross", 850.0), ("W2", "net", 702.0),
              ("W4", "gross", 850.0), ("W5", "gross", 1400.0)]

    def test_letter_conflicts_with_stub_and_css(self):
        c = salary_conflicts(self.VALUES)
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["kind"], "gross")
        self.assertEqual({v[0] for v in c[0]["values"]}, {"W2", "W4", "W5"})

    def test_net_never_compared_with_gross(self):
        c = salary_conflicts(self.VALUES)
        self.assertNotIn(702.0, [v[2] for v in c[0]["values"]])

    def test_within_margin_is_no_conflict(self):
        self.assertEqual(salary_conflicts([("A", "gross", 850.0), ("B", "gross", 900.0)]), [])


class CssMonths(unittest.TestCase):                   # R-8, FR-10
    def test_w4_missing_march_and_april(self):
        required = ["noviembre", "diciembre", "enero", "febrero", "marzo", "abril"]
        self.assertEqual(css_missing_months(["Noviembre", "Diciembre", "Enero", "Febrero"], required),
                         ["marzo", "abril"])


class DraftCheck(unittest.TestCase):                  # R-9, FR-11, S4
    def test_l0412_draft_passes(self):
        self.assertEqual(draft_problems(DRAFT, ITEMS), [])

    def test_amount_and_approval_rejected(self):
        bad = DRAFT + " Tu préstamo de B/. 5,000.00 está aprobado."
        p = draft_problems(bad, ITEMS)
        self.assertIn("contains an amount", p)
        self.assertIn("blocked word: aprobado", p)

    def test_missing_item_rejected(self):
        self.assertIn("missing item: abril", draft_problems(DRAFT.replace(" y abril", ""), ITEMS))


if __name__ == "__main__":
    unittest.main()
