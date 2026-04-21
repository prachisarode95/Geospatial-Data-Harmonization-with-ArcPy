import arcpy
import os
import logging

# -------------------------------
# CONFIGURATION
# -------------------------------

base_folder = r"D:\D drive folders\data_standardization_pipeline"

input_folder = os.path.join(base_folder, "InputData")
gdb_path = os.path.join(base_folder, "data_standardization_pipeline.gdb")

arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True

# Logging
log_file = os.path.join(base_folder, "process.log")
logging.basicConfig(filename=log_file,
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Spatial Reference
target_sr = arcpy.SpatialReference(26910)  # NAD83 UTM Zone 10N


# -------------------------------
# VALIDATION
# -------------------------------

def validate_paths():
    if not arcpy.Exists(gdb_path):
        raise Exception("Geodatabase not found")


# -------------------------------
# CSV CONVERSION
# -------------------------------

def convert_csv():
    try:
        logging.info("Starting CSV conversion...")

        csv_file = os.path.join(input_folder, "CSV", "incidents.csv")

        arcpy.management.XYTableToPoint(
            csv_file,
            "incidents_xy",
            "long",
            "lat",
            coordinate_system=arcpy.SpatialReference(4326)
        )

        logging.info("CSV converted.")

    except Exception as e:
        logging.error(f"CSV conversion failed: {e}")
        raise


# -------------------------------
# MERGE ECW
# -------------------------------

def merge_ecw():
    try:
        logging.info("Merging ECW files...")

        raster_folder = os.path.join(input_folder, "RASTER")
        arcpy.env.workspace = raster_folder

        ecw_files = arcpy.ListRasters("*", "ECW")

        if not ecw_files:
            raise Exception("No ECW files found")

        arcpy.management.MosaicToNewRaster(
            ecw_files,
            gdb_path,
            "merged_ecw",
            pixel_type="8_BIT_UNSIGNED",
            number_of_bands=3
        )

        # 🔴 IMPORTANT RESET
        arcpy.env.workspace = gdb_path

        logging.info("ECW merged.")

    except Exception as e:
        logging.error(f"ECW merge failed: {e}")
        raise


# -------------------------------
# CREATE EXTENT
# -------------------------------

def create_extent():
    try:
        logging.info("Creating extent polygon...")

        desc = arcpy.Describe("merged_ecw")
        extent = desc.extent

        array = arcpy.Array([
            arcpy.Point(extent.XMin, extent.YMin),
            arcpy.Point(extent.XMin, extent.YMax),
            arcpy.Point(extent.XMax, extent.YMax),
            arcpy.Point(extent.XMax, extent.YMin)
        ])

        # 🔴 FIX: assign spatial reference
        polygon = arcpy.Polygon(array, desc.spatialReference)

        arcpy.management.CopyFeatures([polygon], "extent_poly")

        logging.info("Extent created.")

    except Exception as e:
        logging.error(f"Extent creation failed: {e}")
        raise


# -------------------------------
# PROJECT DATA
# -------------------------------

def project_data():
    try:
        logging.info("Projecting data...")

        fc_list = arcpy.ListFeatureClasses()
        logging.info(f"Feature classes: {fc_list}")

        for fc in fc_list:
            if fc.startswith("proj_") or fc == "extent_poly":
                continue

            arcpy.management.Project(fc, f"proj_{fc}", target_sr)

        # 🔴 PROJECT EXTENT ALSO
        arcpy.management.Project("extent_poly", "proj_extent", target_sr)

        logging.info("Projection complete.")

    except Exception as e:
        logging.error(f"Projection failed: {e}")
        raise


# -------------------------------
# CLIP DEM
# -------------------------------

def clip_dem():
    try:
        logging.info("Clipping DEM...")

        dem = os.path.join(input_folder, "RASTER", "092g04_0101_demw.dem")

        dem_desc = arcpy.Describe(dem)
        dem_sr = dem_desc.spatialReference

        if dem_sr.name == "Unknown":
            logging.warning("Defining DEM CRS...")
            arcpy.management.DefineProjection(dem, target_sr)
            dem_sr = target_sr

        arcpy.management.Project(
            "extent_poly",
            "extent_poly_dem",
            dem_sr
        )

        arcpy.management.Clip(
            dem,
            "#",
            os.path.join(gdb_path, "clipped_dem"),
            "extent_poly_dem",
            "#",
            "ClippingGeometry"
        )

        logging.info("DEM clipped.")

    except Exception as e:
        logging.error(f"DEM clip failed: {e}")
        raise


# -------------------------------
# CLIP VECTORS
# -------------------------------

def clip_vectors():
    try:
        logging.info("Clipping vectors...")

        for fc in arcpy.ListFeatureClasses("proj_*"):
            arcpy.analysis.Clip(
                fc,
                "proj_extent",
                f"clip_{fc}"
            )

        logging.info("Vector clipping done.")

    except Exception as e:
        logging.error(f"Vector clip failed: {e}")
        raise


# -------------------------------
# MAIN
# -------------------------------

if __name__ == "__main__":

    try:
        logging.info("===== PIPELINE STARTED =====")

        validate_paths()
        convert_csv()
        merge_ecw()
        create_extent()
        project_data()
        clip_dem()
        clip_vectors()

        logging.info("===== PIPELINE COMPLETED =====")

    except Exception as e:
        logging.critical(f"Pipeline failed: {e}")
        print("Check logs.")
