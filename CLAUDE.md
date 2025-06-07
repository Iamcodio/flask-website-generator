# Claude Code Assistant Guidelines

This document provides guidelines for Claude Code to work efficiently on this Flask website generator project.

## Project Overview

Flask-based website generator with:
- Supabase for production database and authentication
- Local CSV files for development
- Email lead capture with GDPR compliance
- Multi-tier subscription system

## Parallel Task Execution

When working on this project, execute independent tasks in parallel for better performance:

### Examples of Parallel Operations

1. **Multiple File Operations**
   ```
   - Read multiple configuration files simultaneously
   - Generate CSS, HTML, and JavaScript concurrently
   - Process uploaded images in parallel
   ```

2. **Database Operations**
   ```
   - Query user data AND site data at the same time
   - Insert lead data while sending notification email
   - Check subscription status while loading site data
   ```

3. **API Calls**
   ```
   - Fetch Supabase data while checking local files
   - Send emails while updating database
   - Generate site preview while saving to database
   ```

### How to Execute Parallel Tasks

Use multiple tool invocations in a single message:

```xml
<function_calls>
<invoke name="Read">
  <parameter name="file_path">/path/to/file1.py