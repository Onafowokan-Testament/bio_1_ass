from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

CODON_TABLE: Dict[str, tuple[str, str, str]] = {
    "UUU": ("F", "Phe", "Phenylalanine"),
    "UUC": ("F", "Phe", "Phenylalanine"),
    "UUA": ("L", "Leu", "Leucine"),
    "UUG": ("L", "Leu", "Leucine"),
    "UCU": ("S", "Ser", "Serine"),
    "UCC": ("S", "Ser", "Serine"),
    "UCA": ("S", "Ser", "Serine"),
    "UCG": ("S", "Ser", "Serine"),
    "UAU": ("Y", "Tyr", "Tyrosine"),
    "UAC": ("Y", "Tyr", "Tyrosine"),
    "UAA": ("*", "Stop", "Stop"),
    "UAG": ("*", "Stop", "Stop"),
    "UGU": ("C", "Cys", "Cysteine"),
    "UGC": ("C", "Cys", "Cysteine"),
    "UGA": ("*", "Stop", "Stop"),
    "UGG": ("W", "Trp", "Tryptophan"),
    "CUU": ("L", "Leu", "Leucine"),
    "CUC": ("L", "Leu", "Leucine"),
    "CUA": ("L", "Leu", "Leucine"),
    "CUG": ("L", "Leu", "Leucine"),
    "CCU": ("P", "Pro", "Proline"),
    "CCC": ("P", "Pro", "Proline"),
    "CCA": ("P", "Pro", "Proline"),
    "CCG": ("P", "Pro", "Proline"),
    "CAU": ("H", "His", "Histidine"),
    "CAC": ("H", "His", "Histidine"),
    "CAA": ("Q", "Gln", "Glutamine"),
    "CAG": ("Q", "Gln", "Glutamine"),
    "CGU": ("R", "Arg", "Arginine"),
    "CGC": ("R", "Arg", "Arginine"),
    "CGA": ("R", "Arg", "Arginine"),
    "CGG": ("R", "Arg", "Arginine"),
    "AUU": ("I", "Ile", "Isoleucine"),
    "AUC": ("I", "Ile", "Isoleucine"),
    "AUA": ("I", "Ile", "Isoleucine"),
    "AUG": ("M", "Met", "Methionine"),
    "ACU": ("T", "Thr", "Threonine"),
    "ACC": ("T", "Thr", "Threonine"),
    "ACA": ("T", "Thr", "Threonine"),
    "ACG": ("T", "Thr", "Threonine"),
    "AAU": ("N", "Asn", "Asparagine"),
    "AAC": ("N", "Asn", "Asparagine"),
    "AAA": ("K", "Lys", "Lysine"),
    "AAG": ("K", "Lys", "Lysine"),
    "AGU": ("S", "Ser", "Serine"),
    "AGC": ("S", "Ser", "Serine"),
    "AGA": ("R", "Arg", "Arginine"),
    "AGG": ("R", "Arg", "Arginine"),
    "GUU": ("V", "Val", "Valine"),
    "GUC": ("V", "Val", "Valine"),
    "GUA": ("V", "Val", "Valine"),
    "GUG": ("V", "Val", "Valine"),
    "GCU": ("A", "Ala", "Alanine"),
    "GCC": ("A", "Ala", "Alanine"),
    "GCA": ("A", "Ala", "Alanine"),
    "GCG": ("A", "Ala", "Alanine"),
    "GAU": ("D", "Asp", "Aspartic acid"),
    "GAC": ("D", "Asp", "Aspartic acid"),
    "GAA": ("E", "Glu", "Glutamic acid"),
    "GAG": ("E", "Glu", "Glutamic acid"),
    "GGU": ("G", "Gly", "Glycine"),
    "GGC": ("G", "Gly", "Glycine"),
    "GGA": ("G", "Gly", "Glycine"),
    "GGG": ("G", "Gly", "Glycine"),
}

DNA_CHARS = set("ACGT")
RNA_CHARS = set("ACGU")

AA_MASS = {
    "A": 89.09,
    "R": 174.2,
    "N": 132.12,
    "D": 133.1,
    "C": 121.15,
    "Q": 146.15,
    "E": 147.13,
    "G": 75.07,
    "H": 155.16,
    "I": 131.17,
    "L": 131.17,
    "K": 146.19,
    "M": 149.21,
    "F": 165.19,
    "P": 115.13,
    "S": 105.09,
    "T": 119.12,
    "W": 204.23,
    "Y": 181.19,
    "V": 117.15,
}

HYDROPHOBIC = set("AVILMFWY")
ACIDIC = set("DE")
BASIC = set("KRH")


@dataclass
class SequenceDetection:
    seq_type: str
    cleaned_sequence: str
    explanation: str


def extract_sequence(raw_text: str) -> str:
    lines = raw_text.splitlines()
    payload_lines: List[str] = []
    for line in lines:
        striped = line.strip()
        if not striped or striped.startswith(">"):
            continue
        payload_lines.append(striped)

    if not payload_lines and raw_text.strip():
        payload_lines = [raw_text.strip()]

    seq = re.sub(r"\s+", "", "".join(payload_lines)).upper()
    return seq


def detect_sequence_type(sequence: str) -> SequenceDetection:
    if not sequence:
        return SequenceDetection(
            seq_type="Invalid",
            cleaned_sequence="",
            explanation="No sequence was found. Please provide DNA or RNA letters.",
        )

    chars = set(sequence)
    invalid_chars = sorted(
        c for c in chars if c not in DNA_CHARS and c not in RNA_CHARS
    )
    if invalid_chars:
        return SequenceDetection(
            seq_type="Invalid",
            cleaned_sequence=sequence,
            explanation=(
                "The sequence has letters outside biological nucleotide codes: "
                + ", ".join(invalid_chars)
                + "."
            ),
        )

    has_t = "T" in chars
    has_u = "U" in chars

    if has_t and has_u:
        return SequenceDetection(
            seq_type="Invalid",
            cleaned_sequence=sequence,
            explanation="The sequence mixes T and U, so it is neither clean DNA nor clean RNA.",
        )

    if has_t:
        return SequenceDetection(
            seq_type="DNA",
            cleaned_sequence=sequence,
            explanation="The sequence contains T and no U, which is how DNA is identified.",
        )

    return SequenceDetection(
        seq_type="RNA",
        cleaned_sequence=sequence,
        explanation="The sequence contains U and no T, which is how RNA is identified.",
    )


def transcribe_to_mrna(
    sequence: str, seq_type: str, dna_strand_type: Optional[str]
) -> tuple[str, str]:
    if seq_type == "RNA":
        mrna = sequence
        explanation = "Your input was RNA, so transcription output is the same sequence used as mRNA for translation."
        return mrna, explanation

    if dna_strand_type not in {"coding", "template"}:
        raise ValueError(
            "For DNA, choose either Non-template (coding) or Template strand."
        )

    if dna_strand_type == "coding":
        mrna = sequence.replace("T", "U")
        explanation = "You selected the DNA non-template (coding) strand. mRNA is made by replacing T with U while keeping the same base order."
        return mrna, explanation

    complements = {"A": "U", "T": "A", "C": "G", "G": "C"}
    mrna = "".join(complements[b] for b in sequence)
    explanation = "You selected the DNA template strand. mRNA is created by complementary pairing: A->U, T->A, C->G, and G->C."
    return mrna, explanation


def translate_mrna(mrna: str) -> tuple[List[dict], List[dict], str, str]:
    start_index = mrna.find("AUG")
    if start_index == -1:
        explanation = "Translation normally starts at AUG. No AUG codon was found, so no protein chain could be formed."
        return [], [], "", explanation

    codon_rows: List[dict] = []
    amino_rows: List[dict] = []
    protein_letters: List[str] = []

    for idx in range(start_index, len(mrna), 3):
        codon = mrna[idx : idx + 3]
        if len(codon) < 3:
            break

        aa = CODON_TABLE.get(codon)
        if aa is None:
            codon_rows.append(
                {"codon": codon, "one": "?", "abbr": "?", "name": "Unknown"}
            )
            continue

        one, abbr, name = aa
        codon_rows.append({"codon": codon, "one": one, "abbr": abbr, "name": name})

        if one == "*":
            break

        protein_letters.append(one)
        amino_rows.append({"one": one, "abbr": abbr, "name": name})

    protein_sequence = "".join(protein_letters)
    explanation = (
        "Translation started at the first AUG codon and read the mRNA in 3-letter codons. "
        "Each codon was converted to its amino acid until a stop codon or the sequence end."
    )
    return codon_rows, amino_rows, protein_sequence, explanation


def characterize_protein(protein_sequence: str) -> dict:
    if not protein_sequence:
        return {
            "length": 0,
            "molecular_weight": 0.0,
            "isoelectric_point": 0.0,
            "gravy": 0.0,
            "aromaticity": 0.0,
            "explanation": (
                "No protein was produced because translation did not yield a peptide chain."
            ),
        }

    mass = sum(AA_MASS.get(aa, 0.0) for aa in protein_sequence)
    hydrophobic_ratio = round(
        sum(1 for aa in protein_sequence if aa in HYDROPHOBIC) / len(protein_sequence),
        3,
    )
    acidic_count = sum(1 for aa in protein_sequence if aa in ACIDIC)
    basic_count = sum(1 for aa in protein_sequence if aa in BASIC)

    return {
        "length": len(protein_sequence),
        "molecular_weight": round(mass, 2),
        "hydrophobic_ratio": hydrophobic_ratio,
        "acidic_count": acidic_count,
        "basic_count": basic_count,
        "explanation": (
            "A protein is the folded product of the amino-acid chain. "
            "These values summarize your predicted protein's composition and likely chemical behavior."
        ),
    }
