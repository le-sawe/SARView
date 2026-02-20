# -*- coding: utf-8 -*-
import time
import processing
from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsRasterBandStats,
    QgsContrastEnhancement,
    QgsSingleBandGrayRenderer,
    QgsMultiBandColorRenderer,
    Qgis
)
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

import os
import tempfile

def apply_log_scale(input_layer, factor):
    band_count = input_layer.bandCount()
    timestamp = int(time.time())
    temp_files = []
    
    temp_dir = tempfile.gettempdir()

    for band_idx in range(1, band_count + 1):
        instance = QgsRasterCalculatorEntry()
        instance.ref = f'raster@{band_idx}' 
        instance.raster = input_layer
        instance.bandNumber = band_idx
        entries = [instance]
        
        gdal_formula = f"{factor} * log10({instance.ref} + 0.00001)"
        
        out_path = os.path.join(temp_dir, f"sar_log_b{band_idx}_{timestamp}.tif")
        
        calc = QgsRasterCalculator(
            gdal_formula, 
            out_path, 
            "GTiff", 
            input_layer.extent(), 
            input_layer.width(), 
            input_layer.height(), 
            entries,
            QgsProject.instance().transformContext() 
        )
        
        result = calc.processCalculation()
        if result == 0:
            temp_files.append(out_path)
        else:
            print(f"Calculation Error Code on band {band_idx}: {result}")
            return None

    if band_count > 1:
        final_path = os.path.join(temp_dir, f"sar_log_merged_{timestamp}.vrt")
        processing.run("gdal:buildvirtualraster", {
            'INPUT': temp_files,
            'RESOLUTION': 0,
            'SEPARATE': True, 
            'OUTPUT': final_path
        })
    else:
        final_path = temp_files[0]

    log_layer = QgsRasterLayer(final_path, f"{input_layer.name()} (dB)")
    
    if log_layer.isValid():
        QgsProject.instance().addMapLayer(log_layer)
        return log_layer
        
    return None
def apply_outlier_stretch(layer, std_dev_mult, mode, mapping):
    provider = layer.dataProvider()

    def get_enhancement(band_idx):
        if band_idx == -1: return None 
        
        if hasattr(Qgis, 'RasterBandStatistic'):
            stat_flag = Qgis.RasterBandStatistic.All
        else:
            stat_flag = QgsRasterBandStats.All
            
        stats = provider.bandStatistics(band_idx, stat_flag)
        
        low_cut = max(stats.minimumValue, stats.mean - (std_dev_mult * stats.stdDev))
        high_cut = min(stats.maximumValue, stats.mean + (std_dev_mult * stats.stdDev))
        
        enhancement = QgsContrastEnhancement(provider.dataType(band_idx))
        enhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
        enhancement.setMinimumValue(low_cut)
        enhancement.setMaximumValue(high_cut)
        return enhancement

    if mode == "RGB":
        r_band = mapping.get('red', -1)
        g_band = mapping.get('green', -1)
        b_band = mapping.get('blue', -1)
        
        renderer = QgsMultiBandColorRenderer(provider, r_band, g_band, b_band)
        
        if r_band != -1: renderer.setRedContrastEnhancement(get_enhancement(r_band))
        if g_band != -1: renderer.setGreenContrastEnhancement(get_enhancement(g_band))
        if b_band != -1: renderer.setBlueContrastEnhancement(get_enhancement(b_band))
        
    else: # Grayscale
        gray_band = mapping.get('gray', 1)
        renderer = QgsSingleBandGrayRenderer(provider, gray_band)
        renderer.setContrastEnhancement(get_enhancement(gray_band))
    
    layer.setRenderer(renderer)
    layer.triggerRepaint()