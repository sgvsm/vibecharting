#!/bin/bash

# Build deployment package for trend analysis lambda function
# This script creates a zip file with all dependencies

echo "Building trend analysis lambda deployment package..."

# Create a temporary directory for the package
PACKAGE_DIR="trend_analysis_package"
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

# Copy the main lambda function files
cp handler.py $PACKAGE_DIR/
cp database.py $PACKAGE_DIR/
cp requirements.txt $PACKAGE_DIR/

# Copy the analyzers directory
cp -r analyzers $PACKAGE_DIR/

# Copy the utils directory
cp -r utils $PACKAGE_DIR/

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -t $PACKAGE_DIR/

# Create the zip file
echo "Creating deployment package..."
cd $PACKAGE_DIR
zip -r ../trend_analysis_lambda.zip .
cd ..

# Clean up
rm -rf $PACKAGE_DIR

echo "Deployment package created: trend_analysis_lambda.zip"
echo "Package size: $(du -h trend_analysis_lambda.zip | cut -f1)" 