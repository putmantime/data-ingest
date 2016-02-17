<?php
# script that downloads Bio2RDF's life science registry and converts it to JSON for elasticsearch

class lsr 
{
	var $lsr_url = 'https://docs.google.com/spreadsheet/pub?key=0AmzqhEUDpIPvdFR0UFhDUTZJdnNYdnJwdHdvNVlJR1E&single=true&gid=0&output=csv';
	var $lsr_json_file = "../json/lsregistry.json";
	var $lsr_csv_file = "../raw/lsregistry.csv";

	function download()
	{
		file_put_contents($this->lsr_csv_file, file_get_contents($this->lsr_url));
	}

	function generateJSON()
	{
		$mapping = array(
			"Preferred Prefix" => "preferredPrefix",
			"Alt-prefix" => "alternativePrefix",
			"Provider Base URI" => "preferredBaseURI",
			"Alternative Base URI" => "alternativeBaseURI",
			"MIRIAM" => "miriam",
			"BiodbcoreID" => "biodbcore",
			"BioPortal Ontology ID" => "bioportal",
			"thedatahub" => "thedatahub",
			"Abbreviation" => "abbreviation",
			"Title" => "title",
			"Description" => "description",
			"PubMed ID" => "pubmed",
			"Organization" => "organization",
			"Keywords" => "keywords",
			"Homepage" => "homepage",
			"License URL" => "licenseURL",
			"License Text" => "licenseText",
			"ID regex" => "idRegex",
			"ExampleID" => "exampleID",
			"Provider HTML URL" => "providerHtmlTemplate"
		);
		
		$fp = fopen($this->lsr_csv_file,"r");
		$header = fgetcsv($fp, 0, ",", '"');

		$fout = fopen($this->lsr_json_file,"w");
		$id = 1;
		while($a = fgetcsv($fp, 0, ",", '"')) {
			unset($z);
			$z = new stdClass();
			foreach($header AS $k => $v) {
				if(isset($mapping[$v])
						and isset($a[$k]) 
						and $a[$k] != '') {
					$f = $mapping[$v];
					$z->$f = $a[$k];
					if($f == "pubmed" or $f == "alternativePrefix" or $f == "alternativeBaseURI" or $f == "keywords") {
						unset($y);
						$b = explode(",",$a[$k]);
						foreach($b AS $c) {
							$y[] = trim($c);
						}
						$z->$f = $y;
					}
				}
			}
			$z->type = "dataset";
			if(strstr($a[0],".")) {
				// this is a sub-prefix
				$z->type = "subset";
			}
			
			$b = '{"index":{"_index":"prefixcommons","_type":"item","_id":"'.$id++.'"}}'.PHP_EOL.json_encode($z).PHP_EOL;
			fwrite($fout,$b);
		}
		fclose($fp);
		fclose($fout);
	}	
}

$lsr = new lsr();
$lsr->download();
$lsr->generateJSON();

?>