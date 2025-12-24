# Kalki Biochar Data Validation Protocol & Rejection Criteria

## 1. Overview

This document outlines the validation logic, acceptance criteria, and rejection protocols for the Kalki Biochar production process. It is intended to guide the automated or manual review of image data uploaded at various stages of biochar production (Moisture, Start, Middle, 90%, and End).

## 2. Validation Rules by Process Stage

### Stage 1: Wood Moisture Validation

**Objective:** Verify the moisture content of the wood biomass before processing.

* **Approval Criteria:**
  * **Value Check:** Wood moisture reading must be **less than 15%**.
  * **Consistency:** The numeric value entered in the app must match the value displayed on the moisture meter screen in the image.
* **Rejection Criteria:**
  * **High Moisture:** Reading is equal to or greater than 15%.
  * **Mismatch:** The value in the app does not match the image.
  * **Hold Mode:** The moisture meter screen shows "HOLD".
  * **Image Quality:** Image is blurred or unreadable.
  * **Duplicate:** The image has been used previously.
  * **Incorrect Stage:** An image from a different process stage is uploaded.

### Stage 2: Start Process Validation

**Objective:** Verify the initialization of the biochar burn in the Kon-Tiki kiln.

* **Approval Criteria:**
  * **Identification:** The Serial Number painted on the Kon-Tiki kiln must match the Serial Number recorded in the application (e.g., if App says KS5, Kiln must show KS5).
  * **Visual Confirmation:** Biomass must be visible inside the kiln with **fire present**.
* **Rejection Criteria:**
  * **Identification Errors:** Serial number is missing, not visible, or does not match the application data.
  * **Material Issues:** Green (unsuitable) wood is detected; Biomass content is too low; Kiln is filled too much (over 50% biomass).
  * **Visual Issues:** No fire visible; Smoke detected (indicating improper combustion start); Visual obstruction; Blurred image; Cut image (kiln not fully in frame).
  * **Documentation:** Irrelevant document uploaded; Duplicate image.

### Stage 3: Middle Process Validation

**Objective:** Monitor the ongoing combustion process.

* **Approval Criteria:**
  * **Identification:** Serial Number on the kiln must match the Start Process ID.
  * **Status:** Biomass must be visible and filled at least to the middle level.
  * **Combustion:** Fire must be visible.
* **Rejection Criteria:**
  * **Combustion Issues:** Smoke detected; Excess heat; "Hash" (Ash/Char) content is excessive.
  * **Material Issues:** Biomass is very low; Unburnt biomass clearly visible; Content visible outside the Kon-Tiki.
  * **Visual/Technical:** Blurred image; Image cut; Kon-Tiki number not visible or mismatched; Visual obstruction.
  * **Incorrect Stage:** Uploading Start, 90%, or End stage images here.

### Stage 4: 90% Process Validation

**Objective:** Verify the burn is nearing completion (approx. 90% conversion).

* **Approval Criteria:**
  * **Identification:** Serial Number must match the kiln.
  * **Status:** Biomass/Biochar inside the kiln must be clearly visible.
* **Rejection Criteria:**
  * **Coverage:** Biochar coverage is **below 90%** (e.g., < 90% to 75%).
  * **Combustion Issues:** Smoke detected; Excess heat; Hash content is higher than acceptable standards.
  * **Visual/Technical:** Content visible outside the kiln; Kon-Tiki number not visible or mismatched.
  * **Incorrect Stage:** Uploading Start, Middle, or End stage images here.

### Stage 5: End Process Validation

**Objective:** Validate the final biochar product before quenching/collection.

* **Approval Criteria:**
  * **Identification:** Serial Number must match the kiln.
  * **Visibility:** All 4 sides of the Kon-Tiki kiln should be visible in the frame (not a close-up cut).
  * **Content:** Biochar must be clearly visible.
  * **Condition:** **No water** should be visible inside the kiln.
  * **Unit Count:** Only **one** Kon-Tiki kiln should be visible in the image.
* **Rejection Criteria:**
  * **Contamination/Quality:** Water visible inside; Sand visible inside; Unburnt biomass clearly visible; Content collected directly from the ground.
  * **Process Errors:** Multiple Kon-Tiki units in a single image; Kiln filled too much; Content is low.
  * **Combustion:** Smoke visible (process not finished).
  * **Visual/Technical:** Blurred image; Cut image; Visual obstruction; Serial number mismatch or not visible.

---

## 3. Rejection Reason Mapping (System Specifics)

This section details the exact text values used in the rejection dropdown menus for the **Kalki** system versus the **Looker Studio** system. Note that there are slight variations in naming conventions between the two platforms.

### A. Kalki System Rejection Reasons

| Stage                    | Rejection Reason Dropdown Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Moisture**       | • Blurred Image`<br>`• Date Mismatch`<br>`• Duplicate Image Detected`<br>`• Incorrect Stage Image Uploaded`<br>`• Missing Geotag Information`<br>`• Moisture Meter Level Mismatch`<br>`• Timestamp Mismatch`<br>`• Date and Timestamp Mismatched`<br>`• Hold                                                                                                                                                                                                                                                                                            |
| **Start Process**  | • Blurred Image`<br>`• Date Mismatch`<br>`• Duplicate Image Detected`<br>`• Green Wood Detected in Kon Tiki`<br>`• Image Content Not Clearly Visible`<br>`• Incorrect Stage Image Uploaded`<br>`• Missing Geotag Information`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Smoke Detected`<br>`• Timestamp Mismatch`<br>`• Visual Obstruction`<br>`• Kon Tiki Number Not Visible`<br>`• Miss Matched Kontiki Number`<br>`• Line error`<br>`• Cut image`<br>`• Kontiki is filled too much                                 |
| **Middle Process** | • Blurred Image`<br>`• Clearly Visible Outside Kon Tiki`<br>`• Duplicate Image Detected`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Missing Geotag Information`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Smoke Detected`<br>`• Timestamp Mismatch`<br>`• Excess heat`<br>`• Unburnt Biomass Clearly Visible`<br>`• Visual Obstruction`<br>`• Biomass is very low kontiki`<br>`• Hash content is more`<br>`• Error                                |
| **90% Process**    | • Geotag Missing`<br>`• Unburnt Biomass Clearly Visible`<br>`• Content Coverage Below 90%`<br>`• Duplicate Image Detected`<br>`• Smoke Detected`<br>`• Excess Heat or Content Visible Outside Kon Tiki`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Timestamp Mismatch`<br>`• Visual Obstruction`<br>`• Hash content is more`<br>`• Cut image`<br>`• Blur image`<br>`• Cut Image`<br>`• Content not visible |
| **End Process**    | • Blurred Image`<br>`• Content Collected Directly from Ground`<br>`• Water Visible Inside Kon Tiki`<br>`• Unburnt Biomass Clearly Visible`<br>`• Visual Obstruction`<br>`• Date Mismatch`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Sand Visible Inside Kon Tiki`<br>`• Content is low`<br>`• Geotag is Missimg [sic]`<br>`• Cut image`<br>`• Smoke Visible`<br>`• Kontiki is filled too much                |

### B. Looker Studio System Rejection Reasons

| Stage                    | Rejection Reason Dropdown Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Moisture**       | • Blurred Image`<br>`• Date Mismatch`<br>`• Duplicate Image Detected`<br>`• Incorrect Stage Image Uploaded`<br>`• Missing Geotag Information`<br>`• Moisture Meter Level Mismatch`<br>`• Timestamp Mismatch`<br>`• Date and Timestamp Mismatched`<br>`• Hold                                                                                                                                                                                                                                                                                                                                                |
| **Start Process**  | • Blurred Image`<br>`• Date Mismatch`<br>`• Duplicate Image Detected`<br>`• Green Wood Detected in Kon Tiki`<br>`• Image Content Not Clearly Visible`<br>`• Incorrect Stage Image Uploaded`<br>`• Missing Geotag Information`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Smoke Detected`<br>`• Timestamp Mismatch`<br>`• Visual Obstruction`<br>`• Kon Tiki Number Not Visible`<br>`• Excess Heat or Content Visible Outside Kon Tiki`<br>`• Kontiki is filled too much                                                                                                          |
| **Middle Process** | • Blurred Image`<br>`• Clearly Visible Outside Kon Tiki`<br>`• Duplicate Image Detected`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Missing Geotag Information`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Smoke Detected`<br>`• Timestamp Mismatch`<br>`• Unburnt Biomass Clearly Visible`<br>`• Visual Obstruction`<br>`• Biomass is very low kontiki`<br>`• Hash content is more`<br>`• Excess Heat or Content Visible Outside Kon Tiki`<br>`• Kontiki not in shape`<br>`• Green biomass visible |
| **90% Process**    | • Geotag Missing`<br>`• Content Coverage Below 90%`<br>`• Duplicate Image Detected`<br>`• Excess Heat or Content Visible Outside Kon Tiki`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Smoke Detected`<br>`• Timestamp Mismatch`<br>`• Unburnt Biomass Clearly Visible`<br>`• Visual Obstruction                                                                                                                                                                               |
| **End Process**    | • Blurred Image`<br>`• Content Collected Directly from Ground`<br>`• Date Mismatch`<br>`• Incorrect Stage Image Uploaded`<br>`• Kon Tiki Number Mismatch`<br>`• Kon Tiki Number Not Visible`<br>`• Multiple Kon Tiki Units in a Single Image`<br>`• Sand Visible Inside Kon Tiki`<br>`• Content is low`<br>`• Unburnt Biomass Clearly Visible`<br>`• Water Visible Inside Kon Tiki`<br>`• Geotag is Missimg [sic]`<br>`• Hash content is more`<br>`• Kontiki not in shape                                                                                                                    |
