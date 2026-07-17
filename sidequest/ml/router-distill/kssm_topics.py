"""KSSM Form 4/5 topic taxonomy for Biology, Chemistry, Physics.

**v3 (2026-07-18): merges two independent groundings.** v2 (below) was
derived from `ml/rag/extract_toc.py`'s outline/pattern-match extraction.
`TOPIC_GROUNDING_REPORT.md` (dated 2026-07-17, predates this session,
produced by a separate contents-page reading of the same PDFs) largely
CONFIRMED v2's major corrections independently, but also caught what v2
missed:
- Biology Form 4 was missing two entire chapters: Support and Movement in
  Humans and Animals (chapter 14) and Sexual Reproduction, Development and
  Growth in Humans and Animals (chapter 15). Added here.
- "Manufactured Substances in Industry" was placed in Form 5 in v2, based on
  a chapter-4 label inside `00_Chemistry_Form_5_Combined.pdf`. Both
  `TOPIC_GROUNDING_REPORT.md` (reading CHEMISTRY F4.pdf's own contents page)
  AND v2's own extraction (which had directly matched "CHAPTER
  8Manufactured Substances in Industry" inside CHEMISTRY F4.pdf, then
  discarded that in favor of the weaker combined-file evidence) agree it is
  Form 4 chapter 8. Moved back. This means the earlier reasoning in v2 that
  chose the Form 5 placement was wrong; two independent sources beat one.
- "Polymer" is a distinct Form 5 chapter (4), not the same thing as
  Manufactured Substances in Industry; added as its own topic.
- Chemistry Form 4's `chemical_formulae_and_equations` corresponds to a
  specific chapter (3, "The Mole Concept, Chemical Formula and Equation"),
  distinct from `matter_and_atomic_structure` (2) and
  `periodic_table_of_elements` (4); v2 already had these as separate topics,
  so no change needed there, but the chapter numbers are now confirmed.

kssm2 (`dataset/labeled/labeled_kssm2.jsonl`) was generated against v2,
BEFORE this report was found and cross-checked. It is missing the two added
Biology Form 4 topics and has "manufactured_substances_in_industry" rows
tagged as Form 5 that are actually Form 4 content. Known gap, not silently
fixed by relabeling existing rows (that would put text under a label the
teacher never actually saw); close it by generating a kssm3 round against
this file if the track continues.

--- v2 (2026-07-18): grounded in real source material, not hand-drafted
general knowledge. Derived from `ml/rag/index/toc_report.json`, extracted by
`ml/rag/extract_toc.py` from the actual textbooks in `ml/rag/sources/`
(chapter numbers/titles cited per entry below where confidence is high).
See `ml/IMPLEMENTATION_PLAN.md` Phase 2 for the extraction/review process
this went through: this is a human-reviewed correction of a hand-drafted v1,
not a blind auto-merge.

v1 (drafted from general knowledge, before real sources existed) had
systematic placement errors, corrected here:
- Biology: Coordination and Response / Nervous System / Endocrine System is
  a FORM 4 chapter (real TOC: chapter 12 of [DLP] BIOLOGY F4.pdf), not Form
  5 as v1 guessed. Circulatory System, Immunity, and Homeostasis/Urinary
  System were entirely missing from v1's Form 4 list (real chapters 10, 11,
  13). Ecosystem and Environmental Sustainability, which v1 put in Form 4,
  are actually Form 5 (real chapters 9 and 10 of [DLP] BIOLOGY FORM 5.pdf).
- Physics: v1 had Forces/Pressure/Elasticity in Form 4 and Waves/Light in
  Form 5. The real split is the reverse: Waves and Light/Optics are Form 4
  (chapters 5 and 6 of 00_Physics_Form_4_Combined.pdf), Force/Elasticity and
  Forces and Pressure are Form 5 (chapters 1 and 2 of
  00_Physics_Form_5_Combined.pdf). v1 also missed a Form 4 chapter on
  circular motion and gravitation (Kepler's laws, satellite orbits, chapter
  3) and a Form 5 chapter on quantum physics (Planck's constant,
  photoelectric effect, chapter 7) entirely.
- Chemistry: weaker evidence than biology/physics (source PDFs gave
  messier, pattern-matched headings rather than a clean navigable outline;
  see the confidence note on that subject's entries below). Best available
  evidence moved rate_of_reaction/collision_theory from Form 5 to Form 4
  (direct match: "7.4 Collision Theory", CHEMISTRY F4.pdf p.243) and merged
  the old separate "electrochemistry" and "oxidation_reduction" topics into
  one Form 5 topic (real Form 5 chapter 1 treats electron-transfer/redox and
  electrochemistry as a single unit, per
  00_Chemistry_Form_5_Combined.pdf's experiment list).

Each topic gets a short "prompt_hint": phrasing anchors used to help the
query generator produce realistic KSSM-register questions instead of
generic international-textbook phrasing.
"""

# subject -> form -> list of (topic_slug, human label, prompt_hint)
KSSM_TOPICS: dict[str, dict[int, list[tuple[str, str, str]]]] = {
    "biology": {
        4: [
            # [DLP] BIOLOGY F4.pdf, chapters 2, 4 (high confidence: clean
            # pattern-matched chapter numbers with page numbers).
            ("cell_structure_function", "Cell Structure and Function",
             "organelles, plant vs animal cells, unicellular vs multicellular organisation"),
            ("chemical_composition_of_cell", "Chemical Composition of the Cell",
             "water, carbohydrates, proteins, lipids, nucleic acids"),
            # Chapter 3.
            ("movement_of_substances", "Movement of Substances Across the Plasma Membrane",
             "diffusion, osmosis, active transport"),
            # Chapter 5.
            ("metabolism_and_enzymes", "Metabolism and Enzymes",
             "enzyme activity, lock-and-key model, application of enzymes in daily life"),
            # Chapter 6.
            ("cell_division", "Cell Division",
             "mitosis, cell cycle, meiosis"),
            # Chapter 7.
            ("respiration", "Respiration",
             "aerobic respiration, fermentation, energy production"),
            # Chapter 8.
            ("respiratory_system", "Respiratory System",
             "types of respiratory system, mechanism of breathing, gaseous exchange"),
            # Chapter 9.
            ("digestion", "Digestive System and Digestion",
             "digestion, absorption, assimilation, balanced diet"),
            # Chapter 10, MISSING from v1.
            ("circulatory_system", "Circulatory System",
             "human circulatory system, mechanism of heartbeat, blood clotting, blood groups, lymphatic system"),
            # Chapter 11, MISSING from v1.
            ("immunity", "Body Defence and Immunity",
             "body defence mechanisms, antibodies, types of immunity"),
            # Chapter 12, MOVED here from v1's Form 5 (v1 error).
            ("coordination_and_response", "Coordination and Response",
             "nervous system, neurones and synapse, voluntary and involuntary actions, endocrine system"),
            # Chapter 13, MISSING from v1.
            ("homeostasis_and_urinary_system", "Homeostasis and the Urinary System",
             "homeostasis, urinary system"),
            # Chapter 14, MISSING from v1 AND v2 (added in v3 per
            # TOPIC_GROUNDING_REPORT.md's independent contents-page reading).
            ("support_and_movement", "Support and Movement in Humans and Animals",
             "skeletal system, exoskeleton vs endoskeleton, joints and locomotion"),
            # Chapter 15, MISSING from v1 AND v2 (added in v3, same source).
            ("reproduction_development_growth", "Sexual Reproduction, Development and Growth",
             "human reproductive system, fertilisation, growth and development stages"),
        ],
        5: [
            # [DLP] BIOLOGY FORM 5.pdf, chapters 1-4 (clean chapter-numbered TOC).
            ("plant_tissues_and_growth", "Organisation of Plant Tissues and Growth",
             "meristematic tissues, growth curves"),
            ("leaf_structure_function", "Leaf Structure and Function",
             "gaseous exchange, transpiration, photosynthesis, compensation point"),
            ("nutrition_in_plants", "Nutrition in Plants",
             "inorganic nutrients, water and mineral salt uptake"),
            ("transport_in_plants", "Transport in Plants",
             "vascular tissues, translocation, phytoremediation"),
            # Chapter 5. Note: this is PLANT hormones (phytohormone), distinct
            # from Form 4's animal coordination_and_response; do not conflate.
            ("response_in_plants", "Response in Plants",
             "types of responses, phytohormones, application in agriculture"),
            ("sexual_reproduction_in_plants", "Sexual Reproduction in Flowering Plants",
             "flower structure, pollination, fertilisation, seed and fruit development"),
            ("plant_adaptations", "Adaptations of Plants in Different Habitats",
             "structural and physiological adaptations"),
            ("biodiversity", "Biodiversity",
             "classification, naming of organisms, microorganisms and viruses"),
            # Chapter 9, MOVED here from v1's Form 4 (v1 error).
            ("dynamic_ecosystem", "Ecosystem",
             "community and ecosystem, population ecology, energy flow"),
            # Chapter 10, MOVED here from v1's Form 4 (v1 error).
            ("environmental_sustainability", "Environmental Sustainability",
             "threats to the environment, conservation, green technology"),
            ("inheritance", "Inheritance",
             "monohybrid and dihybrid inheritance, genes and alleles, inheritance in humans"),
            ("variation", "Variation",
             "types and factors of variation, mutation"),
            ("genetic_technology", "Genetic Technology",
             "genetic engineering, biotechnology"),
        ],
    },
    "chemistry": {
        # Lower confidence than biology/physics: CHEMISTRY F4.pdf and
        # CHEMISTRY F5.pdf gave messier, pattern-matched headings rather
        # than a clean navigable outline. Treat chapter attributions here as
        # probable, not certain; re-verify against a proper table of
        # contents page if one becomes available.
        4: [
            # Chapter 1 (CHEMISTRY F4.pdf).
            ("introduction_to_chemistry", "Introduction to Chemistry",
             "fields and careers in chemistry, scientific investigation, lab safety"),
            # Chapter 2.
            ("matter_and_atomic_structure", "Matter and Atomic Structure",
             "basic concepts of matter, atomic model, isotopes"),
            ("chemical_formulae_and_equations", "Chemical Formulae and Equations",
             "moles, empirical formula, balancing chemical equations"),
            # Chapter 5 (evidence: "5.2 Ionic Bond", "5.3 Covalent Bond").
            ("chemical_bonds", "Chemical Bonds",
             "ionic bonding, covalent bonding, metallic bonding"),
            ("periodic_table_of_elements", "The Periodic Table of Elements",
             "groups, periods, trends in properties"),
            ("acids_bases_salts", "Acids, Bases and Salts",
             "pH scale, neutralisation, titration, indicators"),
            # Chapter 7, MOVED here from v1's Form 5 (evidence: "7.4
            # Collision Theory", p.243).
            ("rate_of_reaction", "Rate of Reaction",
             "factors affecting reaction rate, collision theory, catalysts"),
            # Chapter 8, MOVED here in v3 from v2's Form 5 (v2 error: see the
            # module docstring; two independent sources agree this is Form
            # 4, "CHAPTER 8Manufactured Substances in Industry" in
            # CHEMISTRY F4.pdf itself).
            ("manufactured_substances_in_industry", "Manufactured Substances in Industry",
             "alloys, ceramics, composite materials, industrial synthesis"),
        ],
        5: [
            # Chapter 1 (00_Chemistry_Form_5_Combined.pdf): merges v1's
            # separate "electrochemistry" and "oxidation_reduction" topics;
            # real content treats electron-transfer/redox and
            # electrochemistry as one unit (voltaic cells, electrolysis,
            # corrosion, extraction and purification of metals).
            ("electrochemistry_and_redox", "Electrochemistry and Redox Reactions",
             "oxidation and reduction, voltaic cells, electrolysis, corrosion, extraction of metals"),
            # Chapter 2.
            ("carbon_compounds", "Carbon Compounds",
             "petroleum, alkanes, alkenes, alcohols, carboxylic acids, esters"),
            # Chapter 3.
            ("thermochemistry", "Thermochemistry",
             "exothermic vs endothermic, heat of precipitation/displacement/neutralisation/combustion"),
            # Chapter 4, ADDED in v3 (distinct from Form 4's Manufactured
            # Substances chapter; TOPIC_GROUNDING_REPORT.md identifies this
            # as its own chapter, not the same topic under a different form).
            ("polymer", "Polymer",
             "natural and synthetic polymers, addition and condensation polymerisation, vulcanisation of rubber"),
            # Chapter 5.
            ("chemicals_for_consumers", "Chemicals for Consumers",
             "soaps, detergents, cleansing action, micelle formation"),
        ],
    },
    "physics": {
        # 00_Physics_Form_4_Combined.pdf, clean chapter-numbered outline.
        4: [
            ("measurement", "Measurement",
             "SI units, precision and accuracy, scalar vs vector quantities"),
            # Chapter 2: v1 split this into two topics (kinematics,
            # dynamics_and_momentum); real content is one chapter.
            ("kinematics_dynamics_momentum", "Force and Motion I",
             "linear motion, Newton's laws, inertia, momentum, conservation of momentum"),
            # Chapter 3, MISSING from v1 entirely.
            ("circular_motion_and_gravitation", "Circular Motion and Gravitation",
             "centripetal force, Kepler's laws, satellite orbits, escape velocity"),
            # Chapter 4.
            ("heat", "Heat",
             "thermal equilibrium, specific heat capacity, latent heat, gas laws"),
            # Chapter 5, MOVED here from v1's Form 5 (v1 error).
            ("waves", "Waves",
             "wave properties, transverse and longitudinal waves, reflection, refraction, diffraction, interference"),
            # Chapter 6, MOVED here from v1's Form 5 (v1 error).
            ("light_and_optics", "Light and Optics",
             "refractive index, total internal reflection, lenses, image formation"),
        ],
        # 00_Physics_Form_5_Combined.pdf, clean chapter-numbered outline.
        5: [
            # Chapter 1, MOVED here from v1's Form 4 (v1 error).
            ("force_and_elasticity", "Force and Elasticity",
             "resultant force, forces in equilibrium, Hooke's law, spring constant"),
            # Chapter 2, MOVED here from v1's Form 4 (v1 error).
            ("forces_and_pressure", "Forces and Pressure",
             "pressure in liquids, Pascal's principle, Archimedes' principle, Bernoulli's principle"),
            ("electricity", "Electricity",
             "current, potential difference, resistance, resistivity, circuits"),
            ("electromagnetism", "Electromagnetism",
             "force on a current-carrying conductor, electromagnetic induction, transformer"),
            ("electronics", "Electronics",
             "cathode rays, rectification, semiconductor diode, transistor"),
            ("nuclear_physics", "Nuclear Physics",
             "radioactive decay, nuclear fission and fusion"),
            # Chapter 7, MISSING from v1 entirely.
            ("quantum_physics", "Quantum Physics",
             "Planck's constant, wave-particle duality, photoelectric effect"),
        ],
    },
}


def all_topics() -> list[dict]:
    """Flatten to a list of {subject, form, slug, label, hint}."""
    out = []
    for subject, forms in KSSM_TOPICS.items():
        for form, topics in forms.items():
            for slug, label, hint in topics:
                out.append(
                    {
                        "subject": subject,
                        "form": form,
                        "slug": slug,
                        "label": label,
                        "hint": hint,
                        "curriculum_topic": f"{subject}_form{form}_{slug}",
                    }
                )
    return out


if __name__ == "__main__":
    topics = all_topics()
    counts: dict[str, int] = {}
    for t in topics:
        key = f"{t['subject']}_form{t['form']}"
        counts[key] = counts.get(key, 0) + 1
    print(f"{len(topics)} topics across {len(counts)} subject/form combinations:")
    for key, n in sorted(counts.items()):
        print(f"  {key}: {n} topics")
