def extract_uniqueness_flags(patient):
    flags = []
    age = int(patient.get("age", 0))
    ldl = float(patient.get("ldl", 0))
    hba1c = float(patient.get("hba1c", 0))
    med_hist = str(patient.get("medical_history", "")).lower()
    meds = str(patient.get("current_medications", "")).lower()
    symptoms = str(patient.get("symptoms", "")).lower()
    bmi = float(patient.get("weight_kg", 0)) / max((float(patient.get("height_cm", 1)) / 100.0) ** 2, 0.1)

    if age < 45 and "chest" in symptoms:
        flags.append("Relatively younger patient with chest symptoms; atypical risk profile needs careful triage.")
    if "kidney" in med_hist or "ckd" in med_hist:
        flags.append("Kidney-related history may alter medication and contrast-use safety decisions.")
    if "diabetes" in med_hist and hba1c >= 7.0:
        flags.append("Long-standing or insufficiently controlled diabetes increases vascular risk burden.")
    if any(x in meds for x in ["warfarin", "apixaban", "rivaroxaban"]) and "aspirin" in meds:
        flags.append("Potential dual antithrombotic overlap detected; bleeding-risk review advised.")
    if bmi >= 30:
        flags.append("Obesity phenotype likely contributes to cardiometabolic and endothelial risk.")
    if "atypical" in symptoms or "jaw" in symptoms or "fatigue" in symptoms:
        flags.append("Atypical symptom expression may mask ischemic disease in early evaluation.")
    if ldl >= 130:
        flags.append("Elevated LDL suggests active atherosclerotic risk and prevention escalation need.")

    if not flags:
        flags.append("No extreme uniqueness signal detected; apply guideline-based stratification with preventive focus.")
    return flags
