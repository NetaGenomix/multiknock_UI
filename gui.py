from flask import Flask, render_template, url_for, request
import os
import json
global goi_path

app = Flask(__name__)

def save_file(file, format=None):
    if file in request.files:
        file = request.files[file]
        if file.filename == '' or (format and not file.filename.endswith(format)):
            return 401
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    else:
        return 400


def get_post_process_params(post_process_params):
        post_process_params['method'] = request.form.get('method')
        genome_by_chr_path = save_file('genome_by_chr_file')
        gff_file_path = save_file('gff_file')
        pam_file_path = save_file('pam_file')
        if genome_by_chr_path == 401 or genome_by_chr_path == 400:
            return f'file genome_by_chr_file was not uploaded or invalid file format'
        if gff_file_path == 401 or gff_file_path == 400:
            return f'file gff_file was not uploaded or invalid file format'
        if pam_file_path == 401 or pam_file_path == 400:
            return f'file pam_file was not uploaded or invalid file format'
        
        post_process_params['genome_by_chr_path'] = genome_by_chr_path
        post_process_params['gff_file_path'] = gff_file_path
        post_process_params['output_name'] = request.form.get('post_process_output_name')
        post_process_params['pam_file_path'] = pam_file_path
        post_process_params['number_of_singletons'] = request.form.get('post_process_number_of_singletons')
        post_process_params['gene_of_interest_file'] = goi_path
        post_process_params['min_distance_threshold'] = request.form.get('min_distance_threshold')
        post_process_params['scoring_function'] = request.form.get('post_process_offt_scoring_function')
        post_process_params['omega'] = request.form.get('post_process_off_t_threshold')
        post_process_params['scoring_function'] = request.form.get('off_target_max_mismatches')
        post_process_params['candidates_per_node'] = request.form.get('candidates_per_node')
        post_process_params['restriction_site'] = request.form.get('restriction_site')
        post_process_params['threads'] = request.form.get('threads')


def get_crispys_parms(crispys_params):
        """
        This function retrieves the CRISPys parameters from the form and stores them in a dictionary.
        Args:
            crispys_params: A dictionary to store the CRISPys parameters
        """
        crispys_params['output_name'] = request.form.get('crispys_output_name')
        crispys_params['design_algorithm'] = request.form.get('design_algorithm')
        crispys_params['where_in_gene'] = request.form.get('where_in_gene')
        crispys_params['off_scoring_function'] = request.form.get('crispys_off_t_func')
        crispys_params['omega'] = request.form.get('crispys_off_t_threshold')
        if goi_path:
            crispys_params['genes_of_interest_file'] = goi_path
        crispys_params['on_scoring_function'] = request.form.get('on_scoring_function')
        crispys_params['internal_node_candidates'] = request.form.get('internal_node_candidates')
        crispys_params['max_target_polymorphic_sites'] = request.form.get('max_target_polymorphic_sites')
        crispys_params['number_of_singletons'] = request.form.get('crispys_number_of_singletons')
        crispys_params['run_for_multiplex'] = request.form.get('run_for_multiplex')
        # Checkboxes: Use request.form.getlist() for checkboxes to retrieve True/False values
        crispys_params['pams'] ='pams' in request.form
        crispys_params['slim_output'] ='slim_output' in request.form
        crispys_params['singletons'] = 'singletons' in request.form


def safe_json_dump(data:dict, path:str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return path


def get_library_parms(data:dict):
        data['main_folder_path'] = request.form.get('main_dir')
        data['family_names_file'] = request.form.get('families_names_file')
        data['crispys_dir_name'] = request.form.get('crispys_dir_name')
        data['post_process_dir_name'] = request.form.get('post_process_dir_name')
        data['library_output_path'] = request.form.get('library_output_path')
        data['organism'] = request.form.get('organism')
     
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
        json_data = {}
        post_process_params = {}
        crispys_params = {}
        json_data['code_path'] = '/groups/itay_mayrose/yaelt1/multiknock/src'
        # Retrieve form json_data
        get_library_parms(json_data)
        app.config['OUTPUT_FOLDER'] = json_data['library_output_path']
        app.config['UPLOAD_FOLDER'] = os.path.join(app.config['OUTPUT_FOLDER'], 'uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Retrieve files
        global goi_path
        goi_path = save_file('genes_of_interest_file', '.csv')
        if goi_path == 401 or goi_path == 400:
            return f'file genes_of_interest_file was not uploaded or invalid file format'

        get_crispys_parms(crispys_params)
        get_post_process_params(post_process_params)
        json_data['global_params']={}
        json_data['global_params']['sparsity'] = request.form.get('sparsity')
      

        json_data['crispys'] = crispys_params
        json_data['post_process'] = post_process_params
        library_name = json_data["post_process"].get("output_name")+"_library"
        # jave json as config
        json_path = safe_json_dump(json_data, os.path.join(json_data["library_output_path"], f"{library_name}_config.json"))

        return f'Configuration file successfully created: {json_path}'
        




if __name__ == '__main__':
    app.run(debug=True)
