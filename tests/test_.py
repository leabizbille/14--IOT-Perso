import unittest
from utils import (
            extraire_piece, 
            nettoyer_Piece
)

class TestFonctionsPieces(unittest.TestCase):

    def test_extraire_piece(self):
        self.assertEqual(extraire_piece("Salon_temperature.csv"), "Salon")
        self.assertIsNone(extraire_piece("FichierSansUnderscore"))

    def test_nettoyer_piece(self):
        self.assertEqual(nettoyer_Piece("   EmmaLit "), "ChambreE")
        self.assertEqual(nettoyer_Piece("Salle à manger"), "Salle_manger")
        self.assertEqual(nettoyer_Piece("Couloir Porte"), "Entree")
        self.assertEqual(nettoyer_Piece("couloir"), "CouloirRDC")
        self.assertEqual(nettoyer_Piece("Autre"), "Autre")
        self.assertIsNone(nettoyer_Piece(123))

if __name__ == "__main__":
    unittest.main()
