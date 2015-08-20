package tunakleague.com.redemption.profiles;

import android.app.Activity;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.app.Fragment;
import android.preference.PreferenceManager;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.StringRequest;
import com.google.gson.JsonObject;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

import tunakleague.com.redemption.DetailedErrorListener;
import tunakleague.com.redemption.HomeActivity;
import tunakleague.com.redemption.MyApplication;
import tunakleague.com.redemption.PreferencesKeys;
import tunakleague.com.redemption.R;
import tunakleague.com.redemption.ServerConstants.*;
import tunakleague.com.redemption.experimental.ExpandableHeightGridView;


/**
 * Displays a user's profile information and allows the user to edit it and save it to the app server.
 */
public class UserFragment extends ProfileFragment {
    public final String TAG = "UserFragment";
    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment UserFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static UserFragment newInstance() {
        UserFragment fragment = new UserFragment();
        Bundle args = new Bundle();
        fragment.setArguments(args);
        return fragment;
    }

    public UserFragment() {
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
        View view = inflater.inflate(R.layout.fragment_user, container, false);

        /*Initialize the skillsField and typesField GridViews*/
        skillsField = (ExpandableHeightGridView) view.findViewById(R.id.skills );
        typesField = (ExpandableHeightGridView) view.findViewById(R.id.types);

        /*Add listeners to the "Add Skills" and "Add Types" buttons*/
        Button skillsAddButton = (Button) view.findViewById(R.id.skills_add);
        Button typesAddButton = (Button) view.findViewById(R.id.types_add);
        skillsAddButton.setOnClickListener(new CreateSkillListener() );
        typesAddButton.setOnClickListener(new CreateTypeListener());

        /*Add listener to the Update button */
        Button updateButton = (Button) view.findViewById(R.id.update_button);
        updateButton.setOnClickListener(new UpdateListener());


        /*Specify all EditText fields in the UI that need to be POPULATED upon retrieving profile info and  and their corresponding server model keys*/
        fieldsToPopulate.put( view.findViewById(R.id.username), USERS.USERNAME.string );
        fieldsToPopulate.put( view.findViewById(R.id.email), USERS.EMAIL.string );
        fieldsToPopulate.put( view.findViewById(R.id.user_summary), USERS.USER_SUMMARY.string );
        fieldsToPopulate.put( view.findViewById(R.id.location), USERS.LOCATION.string );

        /*Specify all EditText fields in the UI that need to be EXTRACTED upon update and their corresponding server model keys*/
        fieldsToExtract.put( view.findViewById(R.id.email), USERS.EMAIL.string );
        fieldsToExtract.put( view.findViewById(R.id.location), USERS.LOCATION.string );
        fieldsToExtract.put( view.findViewById(R.id.user_summary), USERS.USER_SUMMARY.string );

        //TODO: Put in email ONLY if it has changed (probably in updateProfile)

        return view;
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState ){
        super.onActivityCreated(savedInstanceState);
        /*Request needs to be made here since DetailedErrorListener requires Activity context*/
        String url = URLS.USER_LIST.string;

        /*Create request to retrieve the User's profile information from the app server*/
        JsonObjectRequest userProfileRequest = new JsonObjectRequest(Request.Method.GET, url,new JSONObject(),
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject  response) {
                            profileData =  response;
                            populateFields();
                            Log.d(TAG, "Response: " + profileData.toString() );
                    }
                },
                new DetailedErrorListener(getActivity()) //TODO: Need to override and make something to STOP/EXIT the Fragment if request fails (or else you operate on null data)

        )
        {
            @Override
            //Create the headers of the request
            public Map<String, String> getHeaders()
            {
                return MyApplication.getAuthenticationHeader(getActivity());
            }
        };
        MyApplication.requestQueue.add(userProfileRequest);

    }

    @Override
    protected void updateProfile() {
        JSONObject updatedInfo = extractFields(); //Extract required information from UI and place into JSONObject for request body
        Log.d(TAG, updatedInfo.toString());
        /*Create request to update the User's profile*/
        String url = URLS.USER_DETAIL.string;
        JsonObjectRequest updateProfileRequest = new JsonObjectRequest(Request.Method.PUT, url, updatedInfo,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        profileData = response;
                        Toast.makeText(getActivity(), "Personal Profile updated", Toast.LENGTH_LONG).show();
                        Log.d(TAG, "Updated info: " + profileData.toString());
                    }
                }
                ,
                new DetailedErrorListener(getActivity()) //TODO: Need to override and make something to STOP/EXIT the Fragment if request fails (or else you operate on null data)
        )
        {
            @Override
            //Add header of request
            public Map<String, String> getHeaders() {
                return MyApplication.getAuthenticationHeader(getActivity());
            }
        };
        MyApplication.requestQueue.add(updateProfileRequest);

    }


}
