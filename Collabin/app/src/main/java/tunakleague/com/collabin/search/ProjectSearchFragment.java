package tunakleague.com.collabin.search;


import android.os.Bundle;
import android.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;

import tunakleague.com.collabin.R;
import tunakleague.com.collabin.app_constants.ServerConstants;
import tunakleague.com.collabin.experimental.ExpandableHeightGridView;
import tunakleague.com.collabin.profiles.BaseProfileFragment;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link ProjectSearchFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ProjectSearchFragment extends BaseProfileFragment {
    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ProjectSearchFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static ProjectSearchFragment newInstance() {
        ProjectSearchFragment fragment = new ProjectSearchFragment();
        Bundle args = new Bundle();

        fragment.setArguments(args);
        return fragment;
    }

    public ProjectSearchFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.tab_profile, container, false);

        /*Initialize the skillsField*/
        skillsField = (ExpandableHeightGridView) view.findViewById(R.id.skills);
        typesField = (ExpandableHeightGridView) view.findViewById(R.id.types);

        /*Initialize image data, and Add listener to imageview*/
        initializeImageData((ImageView) view.findViewById(R.id.user_image), ServerConstants.USERS.USER_IMAGE.string);

        /*Specify all EditText fields in the UI that need to be POPULATED upon retrieving profile info and  and their corresponding server model keys*/
        fieldsToPopulate.put(view.findViewById(R.id.username), ServerConstants.USERS.USERNAME.string);
        fieldsToPopulate.put(view.findViewById(R.id.email_input), ServerConstants.USERS.EMAIL.string);
        fieldsToPopulate.put(view.findViewById(R.id.user_summary), ServerConstants.USERS.USER_SUMMARY.string );
        fieldsToPopulate.put(view.findViewById(R.id.location), ServerConstants.USERS.LOCATION.string );
        fieldsToPopulate.put(view.findViewById(R.id.last_name_input), ServerConstants.USERS.LAST_NAME.string);
        fieldsToPopulate.put(view.findViewById(R.id.first_name_input), ServerConstants.USERS.FIRST_NAME.string);

        return view;
    }

}
