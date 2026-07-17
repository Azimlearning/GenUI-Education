"""KSSM Form 4/5 topic taxonomy for Biology, Chemistry, Physics.

This is an ILLUSTRATIVE topic scaffold for generating a diverse, curriculum-
scoped training dataset, drafted from general knowledge of the Malaysian KSSM
structure. It is NOT sourced from an official DBP/KPM syllabus document and
should be validated against (or replaced by) the official specification when
available. That validation is exactly what the RAG pipeline in ml/rag/ is
for once real textbook/syllabus source files are supplied: it can ground
these topic labels and future query generation in the actual curriculum text
instead of this hand-drafted list. Track corrections as a diff against this
file, not silent edits, so the provenance stays clear.

Each topic gets a short "prompt_hint": phrasing anchors used to help the
query generator produce realistic KSSM-register questions instead of
generic international-textbook phrasing.
"""

# subject -> form -> list of (topic_slug, human label, prompt_hint)
KSSM_TOPICS: dict[str, dict[int, list[tuple[str, str, str]]]] = {
    "biology": {
        4: [
            ("cell_structure_function", "Cell Structure and Cell Organisation",
             "organelles, plant vs animal cells, cell specialisation"),
            ("cell_division", "Cell Division",
             "mitosis, meiosis, chromosome behaviour"),
            ("movement_of_substances", "Movement of Substances Across the Plasma Membrane",
             "diffusion, osmosis, active transport"),
            ("chemical_composition_of_cell", "Chemical Composition of the Cell",
             "carbohydrates, proteins, lipids, enzymes"),
            ("nutrition", "Nutrition",
             "human digestive system, balanced diet, enzymes in digestion"),
            ("respiration", "Respiration",
             "aerobic vs anaerobic respiration, gas exchange, breathing mechanism"),
            ("dynamic_ecosystem", "Dynamic Ecosystem",
             "energy flow, food webs, population growth, carrying capacity"),
            ("endangered_ecosystem", "Endangered Ecosystem",
             "human impact, biodiversity loss, conservation"),
        ],
        5: [
            ("support_and_movement", "Support and Movement",
             "human skeletal system, plant support tissues"),
            ("coordination_and_response", "Coordination and Response",
             "nervous system, hormones, reflex action, homeostasis"),
            ("reproduction_and_growth", "Reproduction and Growth",
             "human reproductive system, plant reproduction, growth curves"),
            ("genetics_and_heredity", "Genetics and Heredity",
             "Mendelian inheritance, monohybrid cross, dominant/recessive alleles"),
            ("molecular_genetics", "Molecular Genetics",
             "DNA structure, protein synthesis, genetic engineering basics"),
            ("evolution", "Evolution",
             "natural selection, evidence for evolution, speciation"),
            ("human_impact_on_ecosystem", "Human Impact on the Ecosystem",
             "pollution, climate change, sustainable resource use"),
        ],
    },
    "chemistry": {
        4: [
            ("matter", "Matter",
             "states of matter, kinetic theory, changes of state"),
            ("atomic_structure", "The Structure of the Atom",
             "protons, neutrons, electrons, isotopes, electron arrangement"),
            ("periodic_table", "Chemical Formulae and Equations",
             "moles, empirical formula, balancing chemical equations"),
            ("chemical_bonds", "Chemical Bonds",
             "ionic bonding, covalent bonding, metallic bonding"),
            ("electrochemistry", "Electrochemistry",
             "electrolysis, electrolytes, reactivity series"),
            ("acids_bases_salts", "Acids, Bases and Salts",
             "pH scale, neutralisation, titration, indicators"),
            ("periodic_table_of_elements", "The Periodic Table of Elements",
             "groups, periods, trends in properties"),
        ],
        5: [
            ("rate_of_reaction", "Rate of Reaction",
             "factors affecting reaction rate, collision theory, catalysts"),
            ("carbon_compounds", "Carbon Compounds",
             "hydrocarbons, alcohols, carboxylic acids, esters"),
            ("oxidation_reduction", "Oxidation and Reduction",
             "redox reactions, oxidation numbers, displacement reactions"),
            ("thermochemistry", "Thermochemistry",
             "exothermic vs endothermic, heat of reaction, energy diagrams"),
            ("chemicals_for_consumers", "Chemicals for Consumers",
             "soaps, detergents, food additives, medicines"),
            ("manufactured_substances_in_industry", "Manufactured Substances in Industry",
             "polymers, alloys, glass and ceramics, composite materials"),
        ],
    },
    "physics": {
        4: [
            ("measurement", "Measurement",
             "SI units, precision and accuracy, scalar vs vector quantities"),
            ("kinematics", "Force and Motion I",
             "linear motion, velocity, acceleration, graphs of motion"),
            ("dynamics_and_momentum", "Force and Motion I (Momentum and Impulse)",
             "Newton's laws, momentum, impulse, collisions"),
            ("forces_and_pressure", "Force and Pressure",
             "pressure in fluids, Pascal's principle, Archimedes' principle, Bernoulli"),
            ("heat", "Heat",
             "specific heat capacity, latent heat, gas laws"),
            ("elasticity", "Force and Motion (Elasticity)",
             "Hooke's law, elastic potential energy, springs"),
        ],
        5: [
            ("waves", "Waves",
             "wave properties, wave speed, superposition, interference"),
            ("light_and_optics", "Light and Optics",
             "reflection, refraction, lenses, total internal reflection"),
            ("electricity", "Electricity",
             "current, voltage, resistance, circuits, electrical power"),
            ("electromagnetism", "Electromagnetism",
             "magnetic fields, electromagnetic induction, motor effect"),
            ("electronics", "Electronics",
             "semiconductors, diodes, transistors, logic gates"),
            ("nuclear_physics", "Nuclear Physics",
             "radioactivity, half-life, nuclear fission and fusion"),
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
