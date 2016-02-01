import java.util.ArrayList;

/**
 * Created by mcmurry on 11/20/15.
 */
public class Entry {
    public String source = "";
    public String primaryprefix = "";
    public ArrayList<String> resolvingnamespaces = new ArrayList<String>();
    public ArrayList<String> homepages = new ArrayList<String>();
    public String iri = "";
    public String description = "";
    public String title;

    public String toString() {

        StringBuilder allRows = new StringBuilder();

        ArrayList<String> rows = new ArrayList<String>();

        String delim = "\t";

        for (int i = 0; i < resolvingnamespaces.size(); i++) {
            StringBuilder sb = new StringBuilder();
//    Primary Prefix,
            sb.append(primaryprefix);
            sb.append(delim);
//    Alternate Prefix,
            sb.append(delim);
//    Local Identifier,
            sb.append(delim);
//    Entity Identifier (e.g., IRI),
            sb.append(iri);
            sb.append(delim);
//    Identifier namespace path
            sb.append(resolvingnamespaces.get(i));
            sb.append(delim);
//    Identifier Resolution - Computable (y/n),
            sb.append(delim);
//    Identifier Resolution - Human Viewable (y/n),
            sb.append(delim);
//    Alternate Namespace for Human Readable Pages,
            sb.append(delim);
//    Homepage,
            sb.append(homepages.get(i));
            sb.append(delim);
//    Description,
            sb.append(description);
            sb.append(delim);
//    Title,
            sb.append(title);
            sb.append(delim);
//    Source)
            sb.append("Identifiers.org");

            rows.add(sb.toString());
        }

        for (String row : rows) {
            allRows.append("\n");
            allRows.append(row);
        }
        return allRows.toString();

    }

}
