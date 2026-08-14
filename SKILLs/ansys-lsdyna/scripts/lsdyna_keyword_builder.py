# -*- coding: utf-8 -*-
"""
LS-DYNA Keyword Deck (*KEYWORD) 自動生成與校驗工具
提供 *MAT_PIECEWISE_LINEAR_PLASTICITY, *SECTION_SOLID, *CONTACT 等 Keyword Deck 樣板輸出。
"""

class LSDynaDeckBuilder(object):
    def __init__(self, title="LS-DYNA Simulation Model"):
        self.title = title
        self.cards = ["*KEYWORD", "*TITLE", " {}".format(title)]

    def add_material_plasticity(self, mat_id, rho, e, pr, sigy=0.0, etan=0.0):
        """新增 *MAT_PIECEWISE_LINEAR_PLASTICITY (MAT_024)"""
        self.cards.append("*MAT_PIECEWISE_LINEAR_PLASTICITY")
        self.cards.append("$#    mid       rho         e        pr      sigy      etan      fail        td")
        self.cards.append("{:>10d}{:>10.3e}{:>10.3e}{:>10.3f}{:>10.3f}{:>10.3f}{:>10.1f}{:>10.1f}".format(
            mat_id, rho, e, pr, sigy, etan, 0.0, 0.0
        ))

    def add_section_solid(self, sec_id, elform=1):
        """新增 *SECTION_SOLID"""
        self.cards.append("*SECTION_SOLID")
        self.cards.append("$#   secid    elform    aopt")
        self.cards.append("{:>10d}{:>10d}{:>10d}".format(sec_id, elform, 0))

    def add_part(self, part_id, sec_id, mat_id, name="SolidPart"):
        """新增 *PART"""
        self.cards.append("*PART")
        self.cards.append("$# {}".format(name))
        self.cards.append("$#  pid     secid     mid     hgid      adp      opt")
        self.cards.append("{:>10d}{:>10d}{:>10d}{:>10d}{:>10d}{:>10d}".format(
            part_id, sec_id, mat_id, 0, 0, 0
        ))

    def write_deck(self, file_path):
        self.cards.append("*END")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.cards) + "\n")
        print("LS-DYNA Keyword 檔案已成功生成: {}".format(file_path))
        return file_path

if __name__ == "__main__":
    builder = LSDynaDeckBuilder("Impact Test Model")
    builder.add_material_plasticity(mat_id=1, rho=7.85e-9, e=210000.0, pr=0.3, sigy=250.0)
    builder.add_section_solid(sec_id=1, elform=1)
    builder.add_part(part_id=1, sec_id=1, mat_id=1, name="Steel_Beam")
    builder.write_deck("model.k")
