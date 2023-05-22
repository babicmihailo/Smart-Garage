package bm.iot.garage;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentTransaction;

import android.app.NotificationManager;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;

import com.google.android.gms.tasks.Tasks;
import com.google.firebase.FirebaseApp;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ServerValue;
import com.google.firebase.database.ValueEventListener;

import java.util.concurrent.ExecutionException;



public class MainActivity extends AppCompatActivity {

    private PollutionCircleView mPollutionCircleView;


    private String prevStateDoors = "";
    private String prevStateLights = "";
    private String prevStateVents = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView databaseTextView = findViewById(R.id.primer);

        FirebaseApp.initializeApp(this);

        FirebaseDatabase database = FirebaseDatabase.getInstance();
        DatabaseReference ref = database.getReference();

        // Get the parent layout
        FragmentManager fragmentManager = getSupportFragmentManager();
        FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();

        AlertFragment alertFragment = new AlertFragment();
        FireFragment fireFragment = new FireFragment();

        fragmentTransaction.add(R.id.notif, alertFragment);
        fragmentTransaction.add(R.id.notif, fireFragment);
        fragmentTransaction.commit();



        // Attach a listener to the database reference
        ref.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                // Get all the children at this level
                Iterable<DataSnapshot> children = dataSnapshot.getChildren();

                // Create a StringBuilder to hold the data
                StringBuilder sb = new StringBuilder();

                // Iterate over all the children and append their data to the StringBuilder
                for (DataSnapshot child : children) {
                    sb.append(child.getKey() + ": " + child.getValue().toString() + "\n");
                }

                // Set the text of the TextView to the contents of the StringBuilder
                databaseTextView.setText(sb.toString());
            }

            @Override
            public void onCancelled(DatabaseError error) {
                // Failed to read value
                Log.w("TAG", "Failed to read value.", error.toException());
            }
        });

        mPollutionCircleView = findViewById(R.id.pollution_circle);
        DatabaseReference pollutionsRef = database.getReference("pollution");
        pollutionsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                int value = Integer.parseInt(dataSnapshot.getValue(String.class));
                mPollutionCircleView.setPollutionValue(value);
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors here
            }
        });

        DatabaseReference intruderAlert = database.getReference("stateAlarm");
        intruderAlert.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot snapshot) {
                String state = snapshot.getValue(String.class);
                if (state != null && state.equals("on")) {
                    fragmentManager.beginTransaction().show(alertFragment).commit();
                } else {
                    fragmentManager.beginTransaction().hide(alertFragment).commit();
                }
            }

            @Override
            public void onCancelled(DatabaseError error) {

            }
        });

        DatabaseReference fireHazard = database.getReference("stateSprinkler");
        fireHazard.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot snapshot) {
                String state = snapshot.getValue(String.class);
                if (state != null && state.equals("on")) {
                    fragmentManager.beginTransaction().show(fireFragment).commit();
                } else {
                    fragmentManager.beginTransaction().hide(fireFragment).commit();
                }
            }

            @Override
            public void onCancelled(DatabaseError error) {

            }
        });

        // DOORS
        DatabaseReference stateDoorsRef = database.getReference("stateDoors");
        DatabaseReference timestampDoorsRef = database.getReference("timestampDoors");
        Switch doorsSwitch = findViewById(R.id.doors);

        stateDoorsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String state = dataSnapshot.getValue(String.class);
                if (state != null && state.equals("on") && !prevStateDoors.equals(state)) {
                    doorsSwitch.setChecked(true);
                    prevStateDoors = "on";
                } else if (state.equals("off") && !prevStateDoors.equals(state)){
                    doorsSwitch.setChecked(false);
                    prevStateDoors = "off";
                }
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors here
            }
        });

        doorsSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                String state = isChecked ? "on" : "off";
                stateDoorsRef.setValue(state);
                timestampDoorsRef.setValue(ServerValue.TIMESTAMP);

            }
        });

        // LIGHTS
        DatabaseReference stateLightsRef = database.getReference("stateLights");
        DatabaseReference timestampLightsRef = database.getReference("timestampLights");
        Switch lightsSwitch = findViewById(R.id.lights);
        stateLightsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String state = dataSnapshot.getValue(String.class);
                if (state != null && state.equals("on") && !prevStateLights.equals(state)) {
                    lightsSwitch.setChecked(true);
                    prevStateLights = "on";
                } else if (state.equals("off") && !prevStateLights.equals(state)){
                    lightsSwitch.setChecked(false);
                    prevStateLights = "off";
                }
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors here
            }
        });

        lightsSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                String state = isChecked ? "on" : "off";
                stateLightsRef.setValue(state);
                timestampLightsRef.setValue(ServerValue.TIMESTAMP);
            }
        });


        // VENTS
        DatabaseReference stateVentsRef = database.getReference("stateVents");
        DatabaseReference timestampVentsRef = database.getReference("timestampVents");
        Switch ventsSwitch = findViewById(R.id.vents);
        stateVentsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String state = dataSnapshot.getValue(String.class);
                if (state != null && state.equals("on") && !prevStateVents.equals(state)) {
                    ventsSwitch.setChecked(true);
                    prevStateVents = "on";
                } else if (state.equals("off") && !prevStateVents.equals(state)){
                    ventsSwitch.setChecked(false);
                    prevStateVents = "off";
                }
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors here
            }
        });

        ventsSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                String state = isChecked ? "on" : "off";
                stateVentsRef.setValue(state);
                timestampVentsRef.setValue(ServerValue.TIMESTAMP);
            }
        });

        // SPRINKLER
        DatabaseReference stateSprinkerRef = database.getReference("stateSprinker");
        stateVentsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                String state = dataSnapshot.getValue(String.class);
                if (state != null && state.equals("on")) {
                    //ventsSwitch.setChecked(true);
                }

            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors here
            }
        });

    }
}